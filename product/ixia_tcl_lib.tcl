proc check_status {} {
	set root [ixNet getRoot]
	set traffic $root/traffic
	return [ixNet getAttr $traffic -state]
}

proc stop_traffic {} {
	set root [ixNet getRoot]
	set traffic $root/traffic
	return [ixNet exec stop $traffic]
}

proc start_traffic {} {
	set root [ixNet getRoot]
	set traffic $root/traffic
	return [ixNet exec start $traffic]
}

proc clear_statis {} {
	ixNet exec clearStats
}

proc generate_traffic {} {
	#it may take a long time to start all protocols
	ixNet exec startAllProtocols
	set root [ixNet getRoot]
	set traffic $root/traffic
	# get traffic items
	set traffic_item_list [ixNet getList $traffic trafficItem]
	set res {}
	foreach traffic_item $traffic_item_list {
		lappend res [ixNet exec generate $traffic_item]
	}
	set state [ixNet getAttr $traffic -state]
	return [ixNet exec apply $traffic]
}

proc monitor_flow_statistics {item} {
	#'item' designates the statistics item to monitor
	# ixNet help ::ixNet::OBJ-/statistics
	# ixNet getL ::ixNet::OBJ-/statistics view
	# ixNet getL {::ixNet::OBJ-/statistics/view:"Flow Statistics"} page
	# ixNet help {::ixNet::OBJ-/statistics/view:"Flow Statistics"/page}
	# ixNet getA {::ixNet::OBJ-/statistics/view:"Flow Statistics"/page} -columnCaptions
	# ixNet getA {::ixNet::OBJ-/statistics/view:"Flow Statistics"/page} -totalPages
	#define title_list, the title line
	set title_list [ixNet getA {::ixNet::OBJ-/statistics/view:"Flow Statistics"/page} -columnCaptions]  
	#get the index of item in title_list, item is the arguement passed into this tcl script. It can be {Loss %}, {Tx Frame Rate}, or {Rx Frame Rate} and so on
	set index [lsearch $title_list $item]
	#define value, each element of it is a line containing data
	set value [ixNet getA {::ixNet::OBJ-/statistics/view:"Flow Statistics"/page} -rowValues]
	#the structure of value is {{... ...}} {{... ...}} {{... ...}}
	#so we need "eval {set v} $v" to take off its outer list structure
	#create an empty item list
	set item_list {}
	foreach v $value {
	eval {set v} $v
	lappend item_list [lindex $v $index]
	}
	return $item_list
}

proc set_tcl_env {IxTclNetwork_path host_ip} {
	#lappend auto_path "C:/Program Files/Ixia/IxNetwork/6.20-EA/TclScripts/Lib/IxTclNetwork"
	global auto_path
	lappend auto_path $IxTclNetwork_path
	package require IxTclNetwork
	return [ixNet connect $host_ip -port 8009 -version 6.0]
}