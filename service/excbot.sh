#!/bin/bash  
 
d_start()
{
	echo  "Excbot: starting service!" 
	python3 /home/nuked/dev/bot/src/main.py &
    echo $!>/var/run/excbot.pid
   
}
 
d_stop () 
{ 
	echo  "Excbot: stopping Service (PID = $ (cat /var/run/excbot.pid))" 
	kill `cat /var/run/excbot.pid`
	rm  /var/run/excbot.pid
 }
 
d_status () 
{ 
	ps  -ef  |  grep deluged |  grep  -v  grep 
	echo  "PID indicate indication file $ (cat /var/run/excbot.pid 2&gt; / dev / null) " 
}
 
# Some Things That run always 
touch  /var/lock/excbot
 
# Management instructions of the service 
case  "$1"  in 
	start)
		d_start
		;; 
	stop)
		d_stop
		;; 
	restart)
		d_stop
		sleep  1
		d_start
		;; 
	status)
		d_status
		;; 
	* ) 
	echo  "Usage: $ 0 {start | stop | reload | status}" 
	exit  1 
	;; 
esac
 
exit  0