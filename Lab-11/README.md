# About
Date : 22th Dec 2020  
Author: Lionel Gurret  
Description : Deploy Sample war application on Tomcat using Jenkins
# LinkedIn article related
TO COMPLETE
# Prerequisites
This script is designed for Minikube !  
(https://kubernetes.io/fr/docs/tutorials/hello-minikube/ - Click on Launch Terminal)  
# How to run the lab
`git clone https://github.com/gurretl/labs.git`  
`cd labs/Lab-11`  
`./run.sh`

# Manual actions
Once your environment is setup, go to Jenkins and do the following :
* Unlock Jenkins using the unlock key
* Install default plugins
* Create a Jenkins user
* Accept Jenkins default URL

Then, you need to install a plugin in order to deploy a war file in Tomcat.  
* Go to Manage plugins :  
![](images/1.jpg)
* Add the following plugin :  
![](images/2.jpg)
* Now we will create a new job for our task :  
![](images/3.jpg)
* Create the following job :  
![](images/4.jpg)
* Add this repository as SCM :  
![](images/5.jpg)
* Choose to connect only to this subdirectory :  
![](images/6.jpg)
* Configure the following :  
![](images/7.jpg)
* Add a Build step :  
![](images/8.jpg)
* Configure the container as so (create a new user deployer by clicking on Add with the same password as in our Helm chart) :  
![](images/9.jpg)
* Save and run the job by clicking on :  
![](images/10.jpg)
* Your app is deployed, you should see it at the following URL https://TOMCATURL/sample :  
![](images/11.jpg)
