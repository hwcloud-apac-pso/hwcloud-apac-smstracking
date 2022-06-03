# Huawei Cloud Server Migration Service (SMS) Status Tracking using FunctionGraph

## 1.0 Introduction

Server Migration Service (SMS) is a tool that is used for applications and data migration from x86 physical or virtual servers on on-premises or in private or public clouds to Elastic Cloud Servers (ECSs) on Huawei Cloud. It provides advantages such as seamless migration, robust compatibility, high security, and fast transmission which meets most of the user requirements in general.

FunctionGraph hosts and computes event-driven functions in a serverless context while ensuring high availability, high scalability, and zero maintenance. It provides console-based function management with a wide range of supported programming languages including Node.js, Python, Java, Go, PHP, and C#.  The function can be triggered from various Huawei Cloud-native services such as Simple Message Notification (SMN), API Gateway (APIG), Timer, Cloud Trace Service (CTS), Object Storage Service (OBS) trigger, etc. It also works with Log Tank Service (LTS) allowing developers to query run logs of created functions without configuration.

**In this walk-through, we are going to achieve objectives as below:**
* To continuously monitor SMS migration task status using API calls in Function Graph.
* To notify users regarding SMS migration task status via SMN.
* To automatically resume the SMS migration when there is a connection error using API calls.

## 2.0 Solution Overview



*Figure 1: Solution Overview Diagram*

In the case when there is a huge workload (>1TB ) from on-premises, private, or public cloud that needs to be migrated to Huawei Cloud using SMS, a connection error may occur due to an unstable network performance throughout the migration. When the connection between the source server and target server is lost in the middle of migration, an error will be displayed on the SMS console page and users are required to resume back the migration by manually clicking on the start button on the console page. It could be frustrated if the connection is lost at the midnight without the user being aware of it and thus causes the migration to stop until the user resumes back the migration task. This indirectly causes the migration duration longer than expected and unnecessary costs incurred.

The solution as shown in Figure 1 is to solve the problem mentioned. Throughout the SMS migration, the user can track the status of the SMS migration task by calling APIs in developed scripts. The return status of API calls will determine which action will be taken as configured in the scripts. For example, when the return status of API calls is “FAIL”, another API will trigger to automatically resume the migration task in the SMS console page and at the same time will send a notification to users that had subscribed to the SMN services so that they are aware of the action taken. The scripts will be executed on Huawei Cloud-native service FunctionGraph by pre-configuring the runtime environments and triggering events. All the logs of executing the scripts and return statements from scripts will be stored in Log Tank Service (LTS) for further auditing and monitoring purpose.

## 3.0 Pre-requisite

You should have familiarity with the below elements:
•	Elastic Cloud Server (ECS)
•	Server Migration Service (SMS)
•	Simple Message Notification (SMN)
•	Log Tank Service (LTS)
•	API calls in Python Language
Ensure that you have the below elements before getting started:
•	Access Key and Secret Key (AK/SK) obtained from Huawei Cloud Account. The keys can be found under the My Credentials console page. If you work as an IAM user, request the keys from your administrator.
•	Huawei Cloud accounts have the permission to perform workload migration using SMS and access on FunctionGraph, LTS, and SMN. However, it may not apply to IAM users by default as it is according to the policies set by the administrator. For IAM users, ensure that you have all the required resources permission granted for your account from the administrator.

## 4.0 Getting Started

### 4.1 SMS Resource Preparation

In this section, we are going to migrate a workload in TMONE Cloud Alpha Edge (CAE) to Huawei Public Cloud. You may prepare workloads that need to be migrated in your own environment or other cloud environments depending on your needs. The steps are similar and please follow the below instructions for resource creation and migration. You may refer to this link for further details on SMS migration.

Step 1: Create an ECS in TMONE Cloud Alpha Edge (CAE) environments with the specifications as shown in Figure 2.

*Figure 2: TMONE CAE ECS console page*

Step 2: Obtain the command from the Huawei Cloud SMS console as below to download the SMS Agent in created ECS from the previous step as shown in Figure 3.
wget -t 3 -T 15 https://sms-agent-2-0.obs.ap-southeast-1.myhuaweicloud.com/SMS-Agent.tar.gz

*Figure 3: Download the SMS Agent file in created ECS*

Step 3: Start the SMS Agent by inserting the command below. You will ask to enter your Huawei Cloud access and secret key as shown in Figure 4.
tar -zxvf SMS-Agent.tar.gz   && cd SMS-Agent  &&    ./startup.sh

*Figure 4: Starting the SMS agent* 

Step 4: Enter your Huawei Cloud access and secret key in CLI as shown in Figure 5.

*Figure 5: SMS agent AK/SK authentication*
Step 5: Once the SMS Agent is installed and configured successfully, it will automatically register the source server in the Huawei Cloud SMS console. Navigate to the Huawei SMS console page, and observe the created migration task as shown in Figure 6.

*Figure 6: SMS Migration Task in Huawei Cloud SMS console*
Step 6: Configure the target server by using the recommended specifications as shown in Figure 7. Click Create Now to configure the target server.

Figure 7: Recommended specification in SMS
Step 7: Configure the target server by using the recommended specifications as shown in Figure 7. Click Create Now to configure the target server.

Figure 8: Configuring target server using recommended specification
Step 8: Configuring migration task as shown in Figure 9 and click the confirm button.

Figure 9: SMS migration task configuration
Step 9: Review the migration task configuration and click the save button.

Figure 10: Review and save SMS migration task configuration
Step 10: Obtain the migration task ID as shown in Figure 11 for later use.

Figure 11: SMS migration task ID
### 4.2 Python Scripts Preparation

In this section, we are going to set up the API calls in python files. You may obtain the source code of index.py in this huawei-python-sdk folder under Appendix. Open the index.py file, locate the API calls link as below, and replace the migration task ID with the one that had obtained from Section 4.1 Step 10. 

Step 1: To obtain the SMS migration task status by calling API. The return state (READY, RUNNING, ABORTING, ABORT, SYNC_SUCCESS, MIGRATE_FAIL, MIGRATE_SUCCESS) will be used for the action taken in Step 2. URI to query the SMS migration task is as shown below.
GET {sms_region_endpoint}/v3/tasks/{migration_task_id}

*Figure 12: Query SMS migration task ID*
Step 2: To resume the SMS migration task by calling API when the return state from Step 1 is MIGRATE_FAIL. URI to resume the SMS migration task is as shown below.
POST {sms_region_endpoint}/v3/tasks/{migration_task_id}/action

*Figure 13: Resume SMS migration task*

Step 3: To send a notification in terms of SMS/Email to the user regarding the migration task status according to configured conditions. You need to obtain your project id from My Credentials in Huawei Cloud Management Console and SMN urn from the SMN console page. If you do not have a subscription to SMN, please create one. You may refer to the guidelines here.
POST /v2/{project_id}/notifications/topics/{topic_urn}/publish

*Figure 14: SMN notification*
### 4.3 FunctionGraph Setup and Configuration

This section is to configure the environment in FunctionGraph to run the python scripts. 

Step 1: In the Huawei Cloud management console, navigate to the FunctionGraph console. Click create function.

*Figure 15: Create a function in FunctionGraph*

Step 2: Configure the parameter as shown below and click create function.

*Figure 16: Create a function in FunctionGraph*

Step 3: Upload the source code as a local zip file, and put the index.py under the root directory.

*Figure 17: Upload the source code to FunctionGraph*

Step 4: Under the configuration tab, select trigger. Configure the timer to trigger the execution of python scripts.

*Figure 18: Create a timer in FunctionGraph to execute scripts*

Step 5: Under the configuration tab, select environment variables. Configure your access and secret key and check the encrypted box as shown in Figure 19.

*Figure 19: Configure environment variables*
Result Verification

Simulate the environment to do the code testing. Start the migration task in Huawei Cloud by clicking on the start button in the console as shown in Figure 20.

*Figure 20: Configure environment variables*

You may observe the execution logs in Log Tank Service (LTS). In the Huawei Cloud management console, navigate to LTS. Under Log Management, select your function graph log group name. A similar page as shown in Figure 21 will be displayed.

*Figure 21: Execution logs in LTS*

Now, to simulate a connection error, unbinding the EIP from the target server. After a certain duration of time, you will see an error displayed in the console page as shown in Figure 22.

*Figure 22: Error occurs due to connection error*

At the same time, when the function detected that there is an error state return when querying the migration task, it will trigger an API call to resume the migration task and at the same time send a notification to the user.

*Figure 23: Execution logs show the migration task resume automatically when an error detected*

*Figure 24: SMS migration resume successfully*


*Figure 25: Example message notification sent to the user*

## Resource Cleaning

It is good to remove all the resources when it is no longer required to avoid any additional charging fees. 
## Conclusion

In this walk-through, we have learned to track the SMS migration task status using API calls and perform necessary actions such as resuming migration and sending notifications to the users by triggering the corresponding API calls. This solution provides an advantage in that it replaces the manual monitoring and actions taken by users throughout the migration of huge workloads and gets notified when there is anything happening especially when the network performance is unstable.
