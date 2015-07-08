package provide iTest 1.0
package require IxTclNetwork

puts "package IxNetwork has been loaded!"

namespace eval IxNetwork {

proc check {} {
   
   puts "IxNetwork lib is ready"
}
proc ixNetStartQuickTest {} {
    catch {ixNet exec startTestConfiguration} starresult
    if {[string match *OK $starresult]} {
        puts "IxNetWork start testing is successful!"
        after 20000
        ixNetTrackTestPro
    } else {
        puts "IxNetWork start testing is failed!"
    }
}    
proc ixNetTrackTestPro {} {
    set testCfg [ixNetGetTestConfig]
    set testRunning 1
    while {$testRunning} {
        #$testRunning: running - true, not running - false
        #puts "Test is running ......"
        if {![ixNet getAttri $testCfg -testRunning]} {
            set testRunning 0
            ixNet exec stopTestConfiguration
        } 
    }
    after 5000
}
proc ixNetGetTestConfig {} {
    set root [ixNet getRoot]
    set testCfg [ixNet getList $root testConfiguration]
    puts "The testConfiguration is: $testCfg"
    return $testCfg
}  
proc ixNetGetTestresult {} {
    set testCfg [ixNetGetTestConfig]
    set rstDir [ixNet getAttri $testCfg -resultsDir]
    return $rstDir
}
proc rfc2544Throughput {tclServerIP tclServerPort confFileAddr} {
    catch {ixNet connect $tclServerIP -port $tclServerPort } conresult		
    if {[string match *OK $conresult]} {
        puts "Connection to IxNetwork Tcl Server is successful!"
		after 5000
		catch {ixNet exec loadConfig [ixNet readFrom $confFileAddr]} tmpresult
        puts "LoadConfig process is: $tmpresult"
		after 30000
		if {[string match *OK $tmpresult]} {
            puts "Load configuration file is successful!"
            
			set root [ixNet getRoot]
			set testCfg [ixNet getList $root testConfiguration]
			set rfc2544 [ixNet getList $testCfg rfc2544]
            set tput [ixNet getList $rfc2544 throughput]
			after 30000
			catch {ixNet exec startTestConfiguration} starresult
            
			if {[string match *OK $starresult]} {
                puts "IxNetWork start testing is successful!"
				after 20000
				set testRunning 1
				while {$testRunning} {
                    #$testRunning: running - true, not running - false
                    puts "Test is running ......"
					if {![ixNet getAttri $testCfg -testRunning]} {
						set testRunning 0
						ixNet exec stopTestConfiguration
					}
				  after 5000                  
				}
                after 5000
				set rstDir [ixNet getAttri $testCfg -resultsDir]
				puts "Testing result in $tclServerIP"
				puts "Address - $rstDir"
				return $rstDir
			} else {
                puts "IxNetwork can not start testing!"
                
			}
		} else {
            puts "Load configuration file is failed!"
		}
    } else {
        puts "connection is failed, said: $conresult"
	}
    
    catch {ixNet disconnect} discresult
    if {[string match *OK $discresult]} {
        puts "disconnection from IxNetwork Tcl Server is successful!"
    } else {
        puts "Not connected to IxNetwork!"
    }
}
proc commit {} {
    ixNet commit
 }  
proc ixNetConnectTclServer {tclServerIP tclServerPort ixnetVersion} {
    catch {ixNet connect $tclServerIP -version $ixnetVersion -port $tclServerPort} conresult  
    if {[string match *OK $conresult]} {
        puts "Connection to IxNetwork Tcl Server is successful!"
    } else {
        puts "Connection to IxNetwork Tcl Server is failed, said: $conresult"
    }
}
proc ixNetLoadconfigure {confFile path} {
    ixNetClearAllConfig
    catch {ixNet exec loadConfig [ixNet readFrom $path/$confFile.ixncfg]} tmpresult  
    
    if {[string match *OK $tmpresult]} {
        #puts "Load configuration file is successful! $path/$confFile.ixncfg"
    } else {
        puts "Load configuration file is failed, $path/$confFile.ixncfg. said: $tmpresult"
        return 
    }
    #after 15000
    
    set v ""
    foreach v [ixNet getList [ixNet getRoot] vport] {
    	puts "vport($v) - [ixNet getA $v -assignedTo]"
    }
    
    if { $v == "" } {
     	puts "Load configuration file is failed, $path/$confFile.ixncfg. said: $tmpresult"
    	return 
    }
    
    #wait for last vport to be up.
    for { set i 0 } { $i < 30 } { incr i 1 } {
    	set res [ixNet getA $v -state]
    	if { $res == "up" } { break }
    	after 1000
    }
	catch {
		ixTclNet::ClearOwnershipForAllPorts
		ixTclNet::ConnectPorts
	}
	
    puts "Load configuration file is successful! $path/$confFile.ixncfg"
}   
proc ixNetDisconnectTclServer {} {
    catch {ixNet disconnect} conresult  
    if {[string match *OK $conresult]} {
        puts "Disconnection to IxNetwork Tcl Server is successful!"
    } else {
        puts "Disconnection is failed, said: $conresult"
    }
}
proc ixNetClearOwnership {hostname card port} {
    set port [ixNetGetPort $hostname $card $port]
    ixNet execute clearOwnership $port 
    after 3000
}   
proc ixNetGetChassis {hostname} {
    set chassis_s [ixNet getList [ixNet getRoot]/availableHardware chassis]       
    set len [llength $chassis_s]        
    if {$len != 0 && [regexp $hostname $chassis_s]} {
		foreach c $chassis_s {
			if {[regexp $hostname $c]} {
				set chassis $c
			}
		}
    } else {
        set chassis [ixNet add [ixNet getRoot]/availableHardware chassis]
        ixNet setMultiAttrs $chassis \
        -cableLength 0 \
        -masterChassis {} \
        -hostname $hostname
        set chassis [lindex [ixNet remapIds $chassis] 0]
        commit
    }       
    return $chassis
}
#------------------------------------------------------------------------------------------------
# PROCEDURE NAME : ixNetGetPort
# PROCEDURE PURPOSE :
#   This procedure is used to get the ixia chassis's port(not vport) by
#   given the card and port number
#
# PARAMS :
#   hostname    - the host or ip address (eg: 10.170.112.168) of ixia chassis
#   card        - the card number
#   port        - the port number
# NOTE :
#   Not used by java, but used internally by other tcl procedure
#------------------------------------------------------------------------------------------------
proc ixNetGetPort {hostname card port} {
    set chassis [ixNetGetChassis $hostname]
    set cardList [ixNet getFilteredList $chassis card -cardId $card]
    set len [llength $cardList]
    if { $len != 1 } {
        puts stderr "Error"
        return
    }      
    set cardHardware [lindex $cardList 0]      
    set portList [ixNet getFilteredList $cardHardware port -portId $port]     
    set len [llength $portList]
    if { $len != 1 } {
        puts stderr "Error"
        return
    }      
    return [lindex $portList 0]     
}   
proc ixNetAddVPort {} {
    set root [ixNet getRoot]
    set ixNetSG_Stack(0) $root
    set vport [ixNet add $ixNetSG_Stack(0) vport]
    set vport [lindex [ixNet remapIds $vport] 0]
    commit
    return $vport
}
proc ixNetGetVPortByIndex {index} {
    set ports [ixNet getList [ixNet getRoot] vport]
    return [lindex $ports $index]
}    
proc ixNetVportMapToPort {hostname card port} {
    ixNetClearOwnership $hostname $card $port
    set port [ixNetGetPort $hostname $card $port]
    puts "Get the physical port is: $port"
    set vport [ixNetAddVPort]
    puts "Get the virtual port is: $vport"
    ixNet setAtt $vport -connectedTo $port
    commit
    set vport [ixNet remapIds $vport]
    return $vport
}
proc ixNetModifyPortMapping {index hostname card port} {
	
    ixNetClearOwnership $hostname $card $port
    set port [ixNetGetPort $hostname $card $port]
    puts "Get the physical port is: $port"
    set vport [ixNetGetVPortByIndex $index]
    puts "Get the virtual port is: $vport"
    ixNet setAtt $vport -connectedTo $port
	#commit
    #after 5000
	
	if {[info exist ::ontType] && [regexp -nocase "T720" $::ontType] && $index > 0} {
		ixNet setAtt $vport/l1Config/ethernet -speed speed100fd
		ixNet setAtt $vport/l1Config/ethernet -autoNegotiate false
		puts "$vport is set to speed100fd"
		
	} else {
		ixNet setAtt $vport/l1Config/ethernet -speed speed1000
		ixNet setAtt $vport/l1Config/ethernet -autoNegotiate True
		puts "$vport is set to autoNegotiate"
		
	}
	commit
	after 5000
    
    set vport [ixNet remapIds $vport]
    return $vport
}    
proc ixNetClearAllConfig {} {
    ixNet rollback
    ixNet execute newConfig
    #after 10000
}
#------------------------------------------------------------------------------------------------
# PROCEDURE NAME : ixNetConfigPPPoXRole
# PROCEDURE PURPOSE :
#   Get the vport object by index.
#   Add pppox options and set its attribute.
#
# PARAMS : 
#   index       - The index of the vport, start with 0
#   role        - client/server
#------------------------------------------------------------------------------------------------
proc ixNetConfigPPPoXRole {vportIndex role} {
    set vport [ixNetGetVPortByIndex $vportIndex]
    set pppox_opt [ixNet add $vport/protocolStack pppoxOptions]
    ixNet setAtt $pppox_opt -role $role
    commit
}
# --- Add/Get pppox endpoint and range
proc ixNetAddPPPoXEndpoint {vportIndex} {
    set vport [ixNetGetVPortByIndex $vportIndex ]
    set eth [ixNet add $vport/protocolStack ethernet]
    set ppp_ep [ixNet add $eth pppoxEndpoint]
    commit
    set eth [ixNet remapIds $eth]
    set ppp_ep [ixNet remapIds $ppp_ep]
}
proc ixNetGetPPPoXEndpoint {vportIndex} {
    set vport [ixNetGetVPortByIndex $vportIndex]
    set sg_eth [ixNet getList $vport/protocolStack ethernet]
    set sg_pppoxEndpoint [lindex [ixNet getList $sg_eth pppoxEndpoint] 0]
    return $sg_pppoxEndpoint
}  
proc ixNetAddPPPoXEndpointRange {vportIndex} {
    set ppp_ep [ixNetGetPPPoXEndpoint $vportIndex]
    set ppp_ep_rang [ixNet add $ppp_ep range]
    commit 
    set ppp_ep_rang [ixNet remapIds $ppp_ep_rang]
}
#proc ixNetAddPPPoXEndpointRange {vportIndex} {
#    set vport [ixNetGetVPortByIndex $vportIndex]
#    set eth [ixNet add $vport/protocolStack ethernet]
#    set ppp_ep [ixNet add $eth pppoxEndpoint]
#    set ppp_ep_rang [ixNet add $ppp_ep range]
#    commit     
#    set eth [ixNet remapIds $eth]
#    set ppp_ep [ixNet remapIds $ppp_ep]
#    set ppp_ep_rang [ixNet remapIds $ppp_ep_rang]
#}
proc ixNetGetPPPoXEndpointRange {vportIndex} {
    set pppoxEndpoint [ixNetGetPPPoXEndpoint $vportIndex]
    set sg_range [lindex [ixNet getList $pppoxEndpoint range] 0]
    return $sg_range
}
# --- Above   
# --- Add/Get ethernet endpoint and range
proc ixNetAddEthernetEndpoint {vportIndex} {
    set vport [ixNetGetVPortByIndex $vportIndex ]
    set sg_ethernetEndpoint [ixNet add $vport/protocolStack ethernetEndpoint]
    commit
}    
proc ixNetAddEndpintRange {vportIndex} {
    set ethernetEndpoint [ixNetGetEthernetEndpoint $vportIndex]  
    set sg_range [ixNet add $ethernetEndpoint range]    
    commit
}   
proc ixNetGetEthernetEndpoint {vportIndex} {
    set vport [ixNetGetVPortByIndex $vportIndex]
    set sg_ethernetEndpoint  [ixNet getList $vport/protocolStack ethernetEndpoint]
    return $sg_ethernetEndpoint
}
proc ixNetGetEndpointRange {vportIndex} {
    set ethernetEndpoint [ixNetGetEthernetEndpoint $vportIndex]
    set sg_range [lindex [ixNet getList $ethernetEndpoint range] 0]
    return $sg_range
}
# --- Above   
proc ixNetConfigMacRange {vportIndex attributeName attributeValue} {
    #    set sg_range [ixNetGetEndpointRange $vportIndex]
         set sg_range [ixNetGetPPPoXEndpointRange $vportIndex]
         ixNet setMultiAttrs $sg_range/macRange -$attributeName $attributeValue 
         commit
    #   -name {MAC-R1} \
    #   -mac {AA:BB:CC:00:00:00} \
    #   -incrementBy {00:00:00:00:00:01} \
    #   -mtu 1500 \
    #   -count 1
}
proc ixNetConfigVlanRange {vportIndex attributeName attributeValue} {
    #    set sg_range [ixNetGetEndpointRange $vportIndex ]
         set sg_range [ixNetGetPPPoXEndpointRange $vportIndex]
         ixNet setMultiAttrs $sg_range/vlanRange \
         -$attributeName $attributeValue 
         commit
    #       -name {VLAN-R1} \      
    #   -enabled False \
    #   -firstId 1 \
    #   -incrementStep 1 \
    #   -increment 1 \
    #   -uniqueCount 4094 \
    #   -priority 1 \
    #   -tpid {0x8100} \
    #   -innerEnable False \
    #   -innerFirstId 1 \
    #   -innerIncrementStep 1 \
    #   -innerIncrement 1 \
    #   -innerUniqueCount 4094 \
    #   -innerPriority 1 \
    #   -innerTpid {0x8100} \
    #   -idIncrMode 2
}
    
proc ixNetLoadConfig {confFileAddr} {
    catch {ixNet exec loadConfig [ixNet readFrom $confFileAddr]} tmpresult
    
    #after 30000
    if {[string match *OK $tmpresult]} {
        #return 1
    } else {
    	puts "LoadConfig process is: $tmpresult"
        return 0
    }
	ixTclNet::ClearOwnershipForAllPorts
	ixTclNet::ConnectPorts
    set v ""
    foreach v [ixNet getList [ixNet getRoot] vport] {
    	puts "vport($v) - [ixNet getA $v -assignedTo]"
    }
    
    if { $v == "" } {
     	puts "LoadConfig process is: $tmpresult"
    	return 1
    }
    
    #wait for last vport to be up.
    for { set i 0 } { $i < 30 } { incr i 1 } {
    	set res [ixNet getA $v -state]
    	if { $res == "up" } { break }
    	after 1000
    }
    puts "LoadConfig process is: $tmpresult"
    
}
#-trafficItemType l2L3
#-trafficType ipv4
#-enabled true
#-srcDestMesh oneToOne
#-biDirectional True
proc ixNetConfigEndpoint {trafficItemType trafficType enabled srcDestMesh biDirectional} {
    set trafficItems [ixNetGetTrafficItemByIndex 0]
    ixNet setAtt $trafficItems -trafficItemType $trafficItemType
    ixNet setAtt $trafficItems -trafficType $trafficType
    ixNet setAtt $trafficItems -enabled $enabled
    ixNet setAtt $trafficItems -srcDestMesh $srcDestMesh
    ixNet setAtt $trafficItems -biDirectional $biDirectional
    commit
}
#frameSize -type fixed
#frameSize -fixedSize 128
#frameRate -type framesPerSecond
#frameRate -rate 100 
#framePayload -type random
#transmissionControl -type fixedFrameCount
#transmissionControl -frameCount 1000
proc ixNetConfigElement {frameSizetype fixedSize frameRatetype rate framePayloadtype transmissionControltype frameCount} {
    set trafficItem [ixNetGetTrafficItemByIndex 0]
    set cfgElement1 [ixNet getList $trafficItem configElement]
    ixNet setAtt $cfgElement1/frameSize -type $frameSizetype
    ixNet setAtt $cfgElement1/frameSize -fixedSize $fixedSize
    ixNet setAtt $cfgElement1/frameRate -type $frameRatetype
    ixNet setAtt $cfgElement1/frameRate -rate $rate
    ixNet setAtt $cfgElement1/framePayload -type $framePayloadtype
    ixNet setAtt $cfgElement1/transmissionControl -type $transmissionControltype
    ixNet setAtt $cfgElement1/transmissionControl -frameCount $frameCount
    commit
}
proc ixNetConfigTracking {trafficItemIndex trackingby} {
    set trafficItem [ixNetGetTrafficItemByIndex $trafficItemIndex]
    set tracking $trafficItem/tracking
    ixNet setMultiAttrs $tracking \
        -trackBy  "$trackingby"
    commit
}
proc ixNetSetFlowGroup {index baseOn} {
    set configElement [ixNetGetConfigElementByIndex $index]
    set flowgroup $configElement/transmissionDistribution
    ixNet setMultiAttrs $flowgroup \
        -distributions fixedFrameCount
    commit
}   
proc ixNetAddTrafficItem {} {
    set root [ixNet getRoot]
    set trafficItem [ixNet add $root/traffic trafficItem]   
    commit
    set trafficItem [lindex [ixNet remapIds $trafficItem] 0]
    return $trafficItem
}
proc ixNetGetTrafficItemByIndex {index} {
    set trafficItems [ixNet getList [ixNet getRoot]/traffic trafficItem]
    return [lindex $trafficItems $index]
}
proc ixNetGetConfigElementByIndex {index} {
    set trafficItem [ixNetGetTrafficItemByIndex $index]
    set cfgElement [ixNet getList $trafficItem configElement]
    return [lindex $cfgElement $index]
}   
proc ixNetEndPointParser {propertyArrayString} {
    set result ""
    array set parray $propertyArrayString
    foreach i [array names parray] {    
        set port [getVPortByIndex $i]
        set result [concat $result "$port/$parray($i)"]
        puts "$result"  
    }
    return $result
}
proc ixNetAddConfigEndpointSet {sourIndex destIndex} {
    set sg_item [ixNetGetTrafficItemByIndex 0]
    set sg_ep [ixNet add $sg_item endpointSet]
    set sour_ref [ixNetGetVPortByIndex $sourIndex]
    set dest_ref [ixNetGetVPortByIndex $destIndex]
    ixNet setMultiAttrs $sg_ep \
    -sources   [list $sour_ref/protocols]  \
    -destinations  [list $dest_ref/protocols] 
    commit
    set sg_ep [lindex [ixNet remapIds $sg_ep] 0]
}    
proc ixNetStartAllProtocols_uncheckSession {} {
    if { [catch [ixNet exec startAllProtocols async] msg] } {
        puts "Start all protocols successful!"
    } else {
        puts "Failed Start all protocols!"
    }
    #after 12000
}   
proc ixNetStartAllProtocols {} {
    if { [catch [ixNet exec startAllProtocols] msg] } {
        puts "Start all protocols successful!"
    } else {
        puts "Failed Start all protocols!"
    }
}    
proc ixNetStopAllProtocols {} {
    if {[catch [ixNet exec stopAllProtocols] msg]} {
    puts "Stop all protocols successful!"
    } else {
        puts "failed stop all protocols!"
    }
    after 12000
}    
proc ixNetApplyTraffic {} {
    ixNet setAttribute [ixNet getRoot]traffic -refreshLearnedInfoBeforeApply true
    ixNet commit
    update idletasks
    after 5000 
	update idletasks
    
    if {[catch [ixNet exec apply [ixNet getRoot]traffic] msg]} {
        puts "Apply traffic successful!"
    } else {
        puts "Failed to apply traffic, $msg"
    }
    after 10000
}    
proc ixNetStartTraffic {} {
    if {[catch [ixNet exec start [ixNet getRoot]traffic] msg]} {
        puts "Start traffic successful!"
    } else {
        puts "failed to start traffic!"
    }
    #after 10000
}   
proc ixNetStopTraffic {} {
    if {[catch [ixNet exec stop [ixNet getRoot]traffic] msg]} {
        puts "Stop traffic successful!"
    } else {
        puts "failed to Stop traffic!"
    }
    after 5000
}   
proc ixNetClearStatistic {} {
    if {[catch [ixNet exec clearStats] msg]} {
        puts "Clear Statistic successful!"
    } else {
        puts "failed to Clear Statistic!"
    } 
    
    after 3000
}   
# Get all ::ixNet::OBJ-/statistics/view
proc ixNetGetStatisticsViewList {} {
    set root [ixNet getRoot]
    set viewList [ixNet getList $root/statistics view]
    return $viewList
}
# Get the position
# (bin) 70 % lsearch $viewList {::ixNet::OBJ-/statistics/view:"Port Statistics"}
# 0
proc ixNetGetViewIndex {viewName} {
    set root [ixNet getRoot]
    set viewList [ixNet getList $root/statistics view]
    set portView [lsearch $viewList ::ixNet::OBJ-/statistics/view:"$viewName"]
    return $portView   
}    
# (bin) 73 % set port_view_page_id [lindex [ixNet getList $sg_view page] 0]
# ::ixNet::OBJ-/statistics/view:"Port Statistics"/page
proc ixNetGetViewPage {viewName} {
    set viewList [ixNet getList [ixNet getRoot]/statistics view]
    set sg_view [lindex $viewList [ixNetGetViewIndex $viewName]]
    set viewPage [lindex [ixNet getList $sg_view page] 0]
    return $viewPage
}
# Get total rows
# (bin) 75 % set row_count [llength $row_values]
# 2
proc ixNetGetRowCounts {viewName} {    
    set viewPage [ixNetGetViewPage $viewName]   
    set row_values [ixNet getAttribute $viewPage -rowValues]   
    set row_count [llength $row_values]
    return $row_count
}   
# Get row content, if have 2 rows, rowIndex value: 0, 1
# 10.170.112.168/Card05/Port05 Full {1000 Mbps} 1000 859
proc ixNetGetOneRow {viewName rowIndex} {  
    set viewPage [ixNetGetViewPage $viewName]   
    set row_values [ixNet getAttribute $viewPage -rowValues]   
    set one_rowList [lindex $row_values $rowIndex]
    set one_row [lindex $one_rowList 0]
    return $one_row
}
# (bin) 79 % set titles [ixNet getAttri $viewPage -columnCaptions]
# {Stat Name} {Duplex Mode} {Line Speed} {Frames Tx.} {Valid Frames Rx.} 
proc ixNetGetColTitles {viewName} {
    set viewPage [ixNetGetViewPage $viewName]    
    set titles [ixNet getAttri $viewPage -columnCaptions]   
    return $titles
}   
#written by Paul
proc ixNetConfigInterface {vportIndex attributeName attributeValue} {    
    
    set sg_interface [ixNetGetInterface $vportIndex]
    ixNet setMultiAttrs $sg_interface \
    -$attributeName $attributeValue      
    commit
    #-description {Connected - ProtocolInterface - 100:01 - 1} \
    -enabled True \
    -eui64Id {02 00 25 FF FE 4D B5 7D } \
    -mtu 1500 \
    -type default
}
proc ixNetAddInterface {vportIndex} {
    set vport [ixNetGetVPortByIndex $vportIndex ]
    set interface [ixNet add $vport interface]
    commit
    set interface [ixNet remapIds $interface]
}
proc ixNetGetInterface {vportIndex} {
    set vport [ixNetGetVPortByIndex $vportIndex]
    set sg_interface  [lindex [ixNet getList $vport interface] 0]
    return $sg_interface
} 
proc ixNetAddInterfaceVlan {vportIndex} {
    set interface [ixNetGetInterface $vportIndex ]
    set interface_vlan [ixNet add $interface vlan]
    commit
    set interface_vlan [ixNet remapIds $interface_vlan]
}
proc ixNetAddInterfaceIPv4 {vportIndex} {
    set interface [ixNetGetInterface $vportIndex ]
    set interface_ipv4 [ixNet add $interface ipv4]
    commit
    set interface_ipv4 [ixNet remapIds $interface_ipv4]
}
proc ixNetGetInterfaceIPv4 {vportIndex} {
    set vport [ixNetGetVPortByIndex $vportIndex]
    set interface [ixNetGetInterface $vportIndex]
    set sg_interface_ipv4  [lindex [ixNet getList $interface ipv4] 0]
    return $sg_interface_ipv4
} 
proc ixNetConfigInterfaceIPv4 {vportIndex attributeName attributeValue} {    
    set sg_interface_ipv4 [ixNetGetInterfaceIPv4 $vportIndex]
    ixNet setMultiAttrs $sg_interface_ipv4 \
    -$attributeName $attributeValue      
    commit
    #    -gateway 10.10.1.1 \
     -ip 10.10.0.1 \
     -maskWidth 16
}
proc ixNetGetInterfaceVlan {vportIndex} {
    set vport [ixNetGetVPortByIndex $vportIndex]
    set interface [ixNetGetInterface $vportIndex]
    set sg_interface_vlan  [lindex [ixNet getList $interface vlan] 0]
    return $sg_interface_vlan
} 
proc ixNetConfigInterfaceVlan {vportIndex attributeName attributeValue} {    
    set sg_interface_vlan [ixNetGetInterfaceVlan $vportIndex]
    ixNet setMultiAttrs $sg_interface_vlan \
    -$attributeName $attributeValue      
    commit
    #-tpid {0x8100} \
     -vlanCount 1 \
     -vlanEnable True \
     -vlanId {1210} \
     -vlanPriority {0}
}
proc ixNetAddDhcpEndpoint {vportIndex} {
    set vport [ixNetGetVPortByIndex $vportIndex ]
    set eth [ixNet add $vport/protocolStack ethernet]
    set dhcp_ep [ixNet add $eth dhcpEndpoint]
    commit
    set eth [ixNet remapIds $eth]
    set dhcp_ep [ixNet remapIds $dhcp_ep]
}
proc ixNetAddDhcpServerEndpoint {vportIndex} {
    set vport [ixNetGetVPortByIndex $vportIndex ]
    set eth [ixNet add $vport/protocolStack ethernet]
    set dhcpServer_ep [ixNet add $eth dhcpServerEndpoint]
    commit
    set eth [ixNet remapIds $eth]
    set dhcpServer_ep [ixNet remapIds $dhcpServer_ep]
} 
proc ixNetAddDhcpServerEndpointRangeVlanrangePara {vportIndex firstID} {
    set vport [ixNetGetVPortByIndex $vportIndex ]
    set eth [ixNet add $vport/protocolStack ethernet]
    set dhcpServer_ep [ixNet add $eth dhcpServerEndpoint]
    set dhcpServer_ep_rang [ixNet add $dhcpServer_ep range]
    commit
    set eth [ixNet remapIds $eth]
    set dhcpServer_ep [ixNet remapIds $dhcpServer_ep]	
    set dhcpServer_ep_rang [ixNet remapIds $dhcpServer_ep_rang]
    ixNet setMultiAttrs $dhcpServer_ep_rang/vlanRange \
	-enabled True \
	-firstId $firstID
	commit	
}
proc ixNetAddDhcpEndpointRangeVlanrangePara {vportIndex firstID} {
    set vport [ixNetGetVPortByIndex $vportIndex ]
    set eth [ixNet add $vport/protocolStack ethernet]
    set dhcp_ep [ixNet add $eth dhcpEndpoint]
    set dhcp_ep_rang [ixNet add $dhcp_ep range]
    commit
    set eth [ixNet remapIds $eth]
    set dhcp_ep [ixNet remapIds $dhcp_ep]	
    set dhcp_ep_rang [ixNet remapIds $dhcp_ep_rang]
    ixNet setMultiAttrs $dhcp_ep_rang/vlanRange \
	-enabled True \
	-firstId $firstID
	commit	
}   
proc ixNetGetDhcpEndpoint {vportIndex} {
    set vport [ixNetGetVPortByIndex $vportIndex]
    set sg_eth  [ixNet getList $vport/protocolStack ethernet]
    set sg_dhcpEndpoint [lindex [ixNet getList $sg_eth dhcpEndpoint] 0]
    return $sg_dhcpEndpoint
}    
proc ixNetGetDhcpServerEndpoint {vportIndex} {
    set vport [ixNetGetVPortByIndex $vportIndex]
    set sg_eth  [ixNet getList $vport/protocolStack ethernet]
    set sg_dhcpServerEndpoint [lindex [ixNet getList $sg_eth dhcpServerEndpoint] 0]
    return $sg_dhcpServerEndpoint
}       
proc ixNetGetDhcpServerEndpointRange {vportIndex} {
    set DhcpServerEndpoint [ixNetGetDhcpServerEndpoint $vportIndex]
    set sg_range [lindex [ixNet getList $DhcpServerEndpoint range] 0]
    return $sg_range
}
proc ixNetGetDhcpEndpointRange {vportIndex} {
    set DhcpEndpoint [ixNetGetDhcpEndpoint $vportIndex]
    set sg_range [lindex [ixNet getList $DhcpEndpoint range] 0]
    return $sg_range
}
proc ixNetAddDhcpEndpointRange {vportIndex} {
    set dhcp_ep [ixNetGetDhcpEndpoint $vportIndex]
    set dhcp_ep_rang [ixNet add $dhcp_ep range]
    commit 
    set dhcp_ep_rang [ixNet remapIds $dhcp_ep_rang]
}       
proc ixNetAddDhcpServerEndpointRange {vportIndex} {
    set dhcpServer_ep [ixNetGetDhcpServerEndpoint $vportIndex]
    set dhcpServer_ep_rang [ixNet add $dhcpServer_ep range]
    commit 
    set dhcpServer_ep_rang [ixNet remapIds $dhcpServer_ep_rang]
}         
proc ixNetConfigDhcpServerVlanRange {vportIndex attributeName attributeValue} {
    set sg_range [ixNetGetDhcpServerEndpointRange $vportIndex]
    ixNet setMultiAttrs $sg_range/vlanRange \
    -$attributeName $attributeValue 
    commit
    #   -name {VLAN-R1} \      
    #   -enabled False \
    #   -firstId 1 \
    #   -incrementStep 1 \
    #   -increment 1 \
    #   -uniqueCount 4094 \
    #   -priority 1 \
    #   -tpid {0x8100} \
    #   -innerEnable False \
    #   -innerFirstId 1 \
    #   -innerIncrementStep 1 \
    #   -innerIncrement 1 \
    #   -innerUniqueCount 4094 \
    #   -innerPriority 1 \
    #   -innerTpid {0x8100} \
    #   -idIncrMode 2
}        
proc ixNetConfigDhcpClientVlanRange {vportIndex attributeName attributeValue} {
    set sg_range [ixNetGetDhcpEndpointRange $vportIndex]
    ixNet setMultiAttrs $sg_range/vlanRange -$attributeName $attributeValue 
    commit
    #   -name {VLAN-R1} \      
    #   -enabled False \
    #   -firstId 1 \
    #   -incrementStep 1 \
    #   -increment 1 \
    #   -uniqueCount 4094 \
    #   -priority 1 \
    #   -tpid {0x8100} \
    #   -innerEnable False \
    #   -innerFirstId 1 \
    #   -innerIncrementStep 1 \
    #   -innerIncrement 1 \
    #   -innerUniqueCount 4094 \
    #   -innerPriority 1 \
    #   -innerTpid {0x8100} \
    #   -idIncrMode 2
}    
proc ixRemoveChassis {args} {
	set chassis [ ixNet getList [ixNet getRoot]/availableHardware chassis]
	puts "chassis=$chassis"
	if {$chassis!=""} { 
		ixNet remove $chassis
		ixNet commit
	}
}
proc vPortMapToPort {chassisIP uplcard uplport vport_index} {
    set $vport_index [IxNetwork::ixNetVportMapToPort $chassisIP $uplcard $uplport]
    ixNet setMultiAttrs $vport_index -name "$chassisIP:$uplcard:$uplport"
    ixNet commit
}
proc ixNetAddDhcpServer {vportIndex} {
    set vport [ixNetGetVPortByIndex $vportIndex ]
    set eth [ixNet add $vport/protocolStack ethernet]
    set dhcpServer_ep [ixNet add $eth dhcpServerEndpoint]
    commit
    set eth [ixNet remapIds $eth]
    set dhcpServer_ep [ixNet remapIds $dhcpServer_ep]
    set dhcpServer_ep [ixNetGetDhcpServerEndpoint $vportIndex]
    set dhcpServer_ep_rang [ixNet add $dhcpServer_ep range]
    commit 
    set dhcpServer_ep_rang [ixNet remapIds $dhcpServer_ep_rang]
} 
proc ixNetAddDhcpClient {vportIndex} {
    set vport [ixNetGetVPortByIndex $vportIndex ]
    set eth [ixNet add $vport/protocolStack ethernet]
    set dhcp_ep [ixNet add $eth dhcpEndpoint]
    commit
    set eth [ixNet remapIds $eth]
    set dhcp_ep [ixNet remapIds $dhcp_ep]
    set dhcp_ep [ixNetGetDhcpEndpoint $vportIndex]
    set dhcp_ep_rang [ixNet add $dhcp_ep range]
    commit 
    set dhcp_ep_rang [ixNet remapIds $dhcp_ep_rang]
}
proc ixNetCheckProtocolSum {} {

    set viewName "Protocol Summary" 
    set row [IxNetwork::ixNetGetOneRow $viewName 0]
    set name [lindex $row 0]
    set sessionInit [lindex $row 1]
    set sessionsucc [lindex $row 2]
    set sessionfail [lindex $row 3]
    if {$sessionInit == $sessionsucc && $sessionfail == 0} {
        puts Passed
        puts "successed session:$sessionsucc"
    }
}
proc ixNetGetProtocolSum {} {
    after 15000
    set viewName "Protocol Summary" 
    set row [IxNetwork::ixNetGetOneRow $viewName 0]
    set name [lindex $row 0]
    set sessionInit [lindex $row 1]
    set sessionsucc [lindex $row 2]
    set sessionfail [expr $sessionInit - $sessionsucc]
    return "session Initiated:$sessionInit.\nsession succeeded:$sessionsucc.\nsession failed:$sessionfail."
}
proc ixNetChecktrafficPortStat {} {

    set viewName "Port Statistics"
    set row1 [IxNetwork::ixNetGetOneRow $viewName 0]
    set row2 [IxNetwork::ixNetGetOneRow $viewName 1]
    set upname [lindex $row1 0]
    set dnname [lindex $row2 0]
    set upvalidFrametx [lindex $row1 4]
    set dnvalidFrametx [lindex $row2 4]    
    set upvalidFrameRx [lindex $row1 5]
    set dnvalidFrameRx [lindex $row2 5]
    puts "Uplink Valid Frame Tx = $upvalidFrametx"
    puts "Downlink Valid Frame Tx = $dnvalidFrametx"
    puts "Uplink Valid Frame Rx = $upvalidFrameRx"
    puts "Downlink Valid Frame Rx = $dnvalidFrameRx"   
}
proc ixNetChecktrafficItemStat {expFrames} {

    set viewName "Traffic Item Statistics"
    set row [IxNetwork::ixNetGetOneRow $viewName 0]
    set frameloss [lindex $row 4]
    set txframes [lindex $row 1]
    set rxframes [lindex $row 2]    
    if {$rxframes==$expFrames} {
        return passed
    }
    puts $frameloss
}
proc ixNetChecktrafficItemStatFull {row colum} {

    set viewName "Traffic Item Statistics"
    set rownum [IxNetwork::ixNetGetOneRow $viewName $row]
    set value [lindex $rownum $colum]
    puts $value
}
proc ixNetChecktrafficIgmpAggStat {row colum} {

    set viewName "IGMP Aggregated Statistics"
    set rownum [IxNetwork::ixNetGetOneRow $viewName $row]
    set value [lindex $rownum $colum]
    puts $value
}
proc ixNetChecktrafficIgmpQueryAggStat {row colum} {

    set viewName "IGMP Querier Aggregated Statistics"
    set rownum [IxNetwork::ixNetGetOneRow $viewName $row]
    set value [lindex $rownum $colum]
    puts $value
}
proc ixNetChecktrafficItemFrameLoss {} {

    set viewName "Traffic Item Statistics"
    set row [IxNetwork::ixNetGetOneRow $viewName 0]
    set frameloss [lindex $row 4]
    set txframes [lindex $row 1]
    set rxframes [lindex $row 2]    
    puts $frameloss
}
proc ixNetGetObjName { handle } {
    set name [ ixNet getAttribute $handle -name]
    return $name
}
proc ixNetSetObjName { handle name } {
    ixNet setAttribute $handle -name "$name"
    ixNet commit
    puts "Info - [info script] - set name \"$name\" to $handle"
}
proc ixNetEnableCaptureOpt {port data control} {
    set root [ixNet getRoot]
    set vportLst [ixNet getL $root vport]
    foreach vpObj $vportLst {
        set vpName [ixNet getA $vpObj -name]
        set card [lindex [split $vpName :] 1]
        set prt [lindex [split [lindex [split $vpName :] 2] -] 0]
        if {$card < 10} {
            set cardNum [lindex [split $card {}] 1]
        } else {
            set cardNum $card
        }
        if {$prt < 10} {
            set portNum [lindex [split $prt {}] 1]
        } else {
            set portNum $prt
        }
        set prtinfo "$cardNum/$portNum"
        if {$port == $prtinfo} {
            set vp $vpObj  
            if { [catch [ixNet setMultiAttrs $vp/capture -softwareEnabled $control -hardwareEnabled $data] msg] } {
                puts "Successed to enable capture!"
            } else {
                puts "Failed to enable capture!"
            }
            ixNet commit 
        }
    }    
}
proc ixNetStartCapture {} {
    if { [catch [ixNet exec startCapture] msg] } {
        puts "Successed to start capture!"
    } else {
        puts "Failed to start capture!"
    }
    after 12000
} 
proc ixNetStopCapture {} {
    if { [catch [ixNet exec stopCapture] msg] } {
        puts "Successed to stop capture!"
    } else {
        puts "Failed to stop capture!"
    }
    after 12000
}
proc ixNetSaveCapturedFile {dir {name ""} {name2 ""} } {
    variable folder
    set hcnt 0
    set scnt 0
    
    set folder [clock format [clock seconds] -format "%Y_%B_%d_%H_%M_%S"]
    set path $dir/$folder
    file mkdir $path
    cd $dir/$folder
    if { [catch [ixNet exec saveCapture $path] msg] } {
        puts "PASSED - Successed to save captrued packets to $dir and backup file in $path!"
    } else {
        puts "FAILED - Failed to save captured packets!"
    }
    if {$name != ""} {
        cd $dir/$folder
        set fLst [glob *.cap]
        set lo [llength $fLst]
        if { $lo == 2 } {
            for {set i 0} {$i < $lo} {incr i} {
                set filename [lindex $fLst $i]
                set rname [file rootname $filename]
                set b [lindex [split $rname _] 1]
                if {$b == "HW"} {
                    file rename -force $filename ${name}_HW.cap
                    file copy -force $path/${name}_HW.cap $dir/${name}_HW.cap
                } elseif { $b == "SW" } {
                    file rename -force $filename ${name}_SW.cap
                    file copy -force $path/${name}_SW.cap $dir/${name}_SW.cap
                } else {
                    return error
                }
            }
        } elseif { $lo == 4 } {
            for {set i 0} {$i < $lo} {incr i} {
                set filename [lindex $fLst $i]
                set rname [file rootname $filename]
                set b [lindex [split $rname _] 1]
                if {$b == "HW"} {
                    if {$hcnt == 1} {
                            if {$name2 != ""} {
                                file rename -force $filename ${name2}_HW.cap
                                file copy -force $path/${name2}_HW.cap $dir/                                
                                } else {
                                    return "name2 is empty!"
                                }

                        } else {
                            file rename -force $filename ${name}_HW.cap
                            file copy -force $path/${name}_HW.cap $dir/
                            incr cnt 1 
                        }
                } elseif { $b == "SW" } {
                    if {$scnt == 1} { 
                            if {$name2 != ""} {
                                file rename -force $filename ${name2}_HW.cap
                                file copy -force $path/${name2}_HW.cap $dir/                                
                            } else {
                                return "name2 is empty!"
                            }
                        file rename -force $filename ${name2}_SW.cap
                        file copy -force $path/${name2}_SW.cap $dir/
                        incr hcnt 1    
                    } else {
                        file rename -force $filename ${name}_SW.cap
                        file copy -force $path/${name}_SW.cap $dir/
                        incr scnt 1 
                    }                        
                } else {
                    return error
                }
            }
        } elseif { $lo == 0 } {

            puts "no files found"
        } else {
            
            puts "there are more than 4 files in $dir/$folder"
        }
    } else {
        puts "file name is keep unchanged!"
        set fLst [glob *.cap]
        set lo [llength $fLst]
        for {set i 0} {$i < $lo} {incr i} {
            set filename [lindex $fLst $i]
            file copy -force $path/$filename $dir/
        }
    }
    return $folder   
}
proc ixNetSetPortName2 {mode port name {inputs ""}} {
    set str "-mode $mode -port_list $port -port_name_list $name $inputs"
    set rstatus [eval ::ixia::vport_info $str]
    if {[keylget rstatus status] != $::SUCCESS} {
        puts "FAILED - [keylget dhcp_portHandle_status log]"
    } else {
        puts "PASSED!"
    }
}
proc ixNetSetPortName3 {chassisIP card port name index} {

    ixNetClearOwnership $chassisIP $card $port
    set vport [ixNetGetVPortByIndex $index]
    puts "Get the virtual port is: $vport"
    ixNet setAtt $vport -name $name
    ixNet setAtt $vport -connectionInfo $name

    ixNet commit
}
proc ixNetSetPortName {chasIP card port name } {

    set root [ixNet getRoot]
    set portList [ixNet getL $root vport]
    set portinfo "::ixNet::OBJ-/availableHardware/chassis:\"$chasIP\"/card:$card/port:$port"
    puts $portinfo
    foreach vport $portList {          
        set connectinfo [ixNet getA $vport -connectedTo]
        puts $connectinfo
        if {$connectinfo == $portinfo} {
                ixNet setAtt $vport -name $name
                ixNet commit
        }
    }               
}
}




