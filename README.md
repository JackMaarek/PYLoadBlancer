# PYLoadBlancer
A Simple Load Balancer

Trying to make a load balancer with python based on three simple principles between the LB and my backends/Apps

1- HealthCheck most commonly heartbeat ( This would be in datagram UDP protocol because we don't need to know if the alive flag is recieved )
2 - Enrollement if HealthCheck is good ( by getting the health status on the heart beat dictionnary) 
3 - TCP socket in order to be sure that messages sent are recieved from server/client 
