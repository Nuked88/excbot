#! / bin / bash  
# /usr/local/bin/deluge.sh 

 
function d_start ( ) 
{ 
	echo  "Excbot: starting service!" 
	python3 /home/nuked/dev/bot/src/main.py --pidfile = /tmp/excbot.pid #REPLACE THE PATH
	 sleep  5 
	echo  "PID is $ (cat /tmp/excbot.pid) " 
}
 
function d_stop ( ) 
{ 
	echo  "Excbot: stopping Service (PID = $ (cat /tmp/excbot.pid) )" 
	kill $ ( cat  /tmp/excbot.pid ) 
	rm  /tmp/excbot.pid
 }
 
function d_status ( ) 
{ 
	ps  -ef  |  grep deluged |  grep  -v  grep 
	echo  "PID indicate indication file $ (cat /tmp/excbot.pid 2&gt; / dev / null) " 
}
 
# Some Things That run always 
touch  /var/lock/excbot
 
# Management instructions of the service 
box  "$ 1"  in 
	start )
		d_start
		;; 
	Stop )
		d_stop
		;; 
	Reload )
		d_stop
		sleep  1
		d_start
		;; 
	Status )
		d_status
		;; 
	* ) 
	Echo  "Usage: $ 0 {start | stop | reload | status}" 
	exit  1 
	;; 
esac
 
exit  0