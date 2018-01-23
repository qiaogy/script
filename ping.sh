#!/bin/bash

function f1(){
    if [ $1 == 'yes' ];then
	    ping -c 3 www.baidu.com;
    else
	    pinga
    fi
}



f1 $1
