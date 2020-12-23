# About
Date : 22th Dec 2020  
Author: Lionel Gurret  
Description : Deploy Sample war application on Tomcat using Jenkins
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
Go to Manage plugins :  
<img src="images/1.jpg" width="500" >    

Add the following plugin :  
<img src="images/2.jpg" width="500" >  

Now we will create a new job for our task :  
<img src="images/3.jpg" width="500" >  

Create the following job :  
<img src="images/4.jpg" width="500" >  

Add this repository as SCM :  
<img src="images/5.jpg" width="500" >  

Choose to connect only to this subdirectory :  
<img src="images/6.jpg" width="500" >  

Configure the following :  
<img src="images/7.jpg" width="500" >  

Add a Build step :  
<img src="images/8.jpg" width="500" >  

Configure the container as so (create a new user deployer by clicking on Add with the same password as in our Helm chart) :  
<img src="images/9.jpg" width="500" >  

Save and run the job by clicking on :  
<img src="images/10.jpg" width="200" >  

Your app is deployed, you should see it at the following URL https://TOMCAT_URL/sample :  
<img src="images/11.jpg" width="500" >  
