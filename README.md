
# Comprehensive Guide to Building a Reddit ETL Pipeline for US Elections Sentiment Analysis

This guide will walk you through the complete process of creating an ETL (Extract, Transform, Load) pipeline that extracts data from the Reddit API, performs sentiment analysis using TextBlob, and uploads the processed data to AWS S3. We will set everything up on an AWS EC2 instance, ensuring all steps are clear and thorough.

## 1. Create and Configure AWS EC2 Instance

### Step 1: Launch an EC2 Instance

1.  **Access the AWS Management Console**: Log into your AWS account and navigate to the EC2 Dashboard.
2.  **Launch Instance**:
    -   Click on **Launch Instance** to start the setup.
    -   **Choose an Amazon Machine Image (AMI)**: Select the latest version of Ubuntu Server for compatibility with the packages we will install.
    -   **Select Instance Type**: Choose an instance type (e.g., **t2.micro**) that falls under the free tier for testing purposes.
    -   **Configure Instance**: Adjust the settings as needed. You can leave most settings as default unless specific network configurations are required.
    -   **Add Storage**: The default storage (e.g., 8 GB) is usually sufficient for this project, but you can adjust it based on your needs.
    -   **Configure Security Group**: Create a new security group that allows SSH (port 22) access from your IP address. This is essential for accessing your instance remotely.
    -   **Key Pair**: Select an existing key pair or create a new one (e.g., `your-key.pem`) for SSH access.
3.  **Launch the Instance**: Review your configurations and click **Launch** to create the instance.

### Step 2: SSH into EC2 Instance

1.  **Open Putty**:
    
    -   Convert your `.pem` key file to a `.ppk` file using Puttygen if you haven't done so already.
    -   In Putty, enter the public IP address of your EC2 instance as the Host Name.
2.  **Configure SSH Authentication**:
    
    -   Go to **Connection > SSH > Auth** and browse for your `.ppk` file.
3.  **Connect**:
    
    -   Click **Open** to initiate the SSH session. If prompted, accept the security alert regarding the server's host key.
    -   You should see a terminal window where you can log in as `ubuntu`.
4.  **Update and Upgrade the System**:
    
    -   Once logged in, ensure your instance is up to date:
  
        `sudo apt update && sudo apt upgrade -y` 
        

## 2. Install and Configure AWS CLI

### Step 1: Install AWS CLI

1.  **Install AWS CLI**: This tool allows you to interact with AWS services from your command line.

    `sudo apt install awscli -y` 
    

### Step 2: Configure AWS CLI

1.  **Run AWS Configuration**:
    
    -   Execute the following command:
    

    `aws configure` 
    
    -   You will be prompted to enter your AWS credentials and preferences:
        -   **AWS Access Key ID**: Your access key from the AWS IAM dashboard.
        -   **AWS Secret Access Key**: Your secret key from the AWS IAM dashboard.
        -   **Default region name**: Enter your preferred AWS region (e.g., `us-east-1`).
        -   **Default output format**: You can choose `json`, `text`, or `table`, but `json` is recommended for ease of use.

### Step 3: Create an IAM Role for EC2

1.  **Navigate to IAM Dashboard**:
    -   In the AWS Management Console, go to the IAM Dashboard.
2.  **Create a Role**:
    -   Click on **Roles** in the sidebar, then click **Create role**.
    -   Choose **EC2** as the trusted entity since you want to grant this role permissions for your EC2 instance.
    -   **Attach Permissions**: Search for and select the **AmazonS3FullAccess** policy to allow your instance to interact with S3 buckets.
3.  **Complete Role Creation**:
    -   Give your role a name (e.g., `EC2_S3_Access`) and complete the creation process.
4.  **Attach IAM Role to EC2 Instance**:
    -   Go back to the EC2 Dashboard, select your instance, and click on **Actions > Security > Modify IAM role**.
    -   Attach the newly created IAM role to your EC2 instance.

## 3. Create AWS S3 Bucket

### Step 1: Set Up an S3 Bucket

1.  **Navigate to S3**: In the AWS Management Console, go to the S3 service.
2.  **Create a Bucket**:
    -   Click on **Create bucket**.
    -   **Bucket Name**: Choose a globally unique name for your bucket (e.g., `reddit-etl-chinmayi`).
    -   **Region**: Select the same region you used for your EC2 instance for easier access.
    -   **Permissions**: Adjust the bucket permissions as needed, ensuring that your EC2 instance can access it.
3.  **Finalize Creation**: Click on **Create bucket** to finish the process.

## 4. Set Up the ETL Pipeline

### Step 1: Install Required Python Packages

1.  **Install Python Package Manager (pip)**:
    
    -   If Python 3 is not installed, install it along with pip:
    
    
    
    
    
    `sudo apt install python3-pip -y` 
    
2.  **Install Necessary Packages**:
    
    -   Install the required Python packages for our ETL process:
    
    
    
    
    
    `pip3 install requests pandas textblob boto3` 
    

### Step 2: Create the Reddit ETL Script (Reddit_etl.py)

This Python script will handle the extraction of data from Reddit, transform it by performing sentiment analysis, and load it into your S3 bucket.

1.  **Create the Python Script**:
    
    -   Create a new file named `Reddit_etl.py`:
    
    
    
    
    
    `nano Reddit_etl.py` 
    
    -   Copy and paste the following code into the file:
    
    python
    
    
    
    `import requests
    import requests.auth
    import pandas as pd
    from textblob import TextBlob
    
    def reddit_Extraction():
        CLIENT_ID = '2v7MESwQm_3Xu1hkYygkSQ'
        SECRET_KEY = 'a5dMZ27skiv8qd0aclw0HAuovHnBFA'
        USERNAME =  'Chinmayi_Prakash'
        PASSWORD = 'Chinthan031*'
    
        # Authentication
        auth = requests.auth.HTTPBasicAuth(CLIENT_ID, SECRET_KEY)
        data = {
            'grant_type': 'password',
            'username': USERNAME,
            'password': PASSWORD
        }
        headers = {'User-Agent': 'MyAPI/0.0.1'}
    
        url = 'https://www.reddit.com/api/v1/access_token'
        res = requests.post(url, auth=auth, data=data, headers=headers)
        TOKEN = res.json()['access_token']
    
        headers['Authorization'] = f'bearer {TOKEN}'
    
        # Fetch posts
        request_url = 'https://oauth.reddit.com/r/Ask_Politics/hot'
        res = requests.get(request_url, headers=headers)
    
        posts = []
        for post in res.json()['data']['children']:
            selftext = post['data']['selftext']
            sentiment = TextBlob(selftext).sentiment.polarity
            sentiment_label = 'positive' if sentiment > 0 else 'negative' if sentiment < 0 else 'neutral'
            
            posts.append({
                'subreddit': post['data']['subreddit'],
                'title': post['data']['title'],
                'sentiment': sentiment_label,
                'upvote_ratio': post['data']['upvote_ratio'],
                'ups': post['data']['ups'],
                'downs': post['data']['downs'],
                'score': post['data']['score']
            })
        
        df = pd.DataFrame(posts)
        
        # Upload CSV to S3
        df.to_csv('s3://reddit-etl-chinmayi/reddit.csv', index=False)
        print(df)` 
    
    -   Save and exit the editor (press `CTRL + X`, then `Y`, and `Enter`).

### Step 3: Create Airflow DAG (Reddit_dag.py)

This script sets up an Apache Airflow DAG (Directed Acyclic Graph) to automate the execution of the Reddit ETL process.

1.  **Create the Airflow DAG File**:
    
    -   Create a new file named `Reddit_dag.py`:
    
    
    
    
    
    `nano Reddit_dag.py` 
    
    -   Copy and paste the following code into the file:
    
    python
    
    
    
    `from datetime import timedelta
    from airflow import DAG
    from airflow.operators.python_operator import PythonOperator
    from airflow.utils.dates import days_ago
    from datetime import datetime
    from Reddit_etl import reddit_Extraction
    
    default_args = {
        'owner': 'Chinmayi',
        'depends_on_past': False,
        'start_date': datetime(2020, 11, 8),
        'email': ['chinmayiprakashmurthy@gmail.com'],
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=1)
    }
    
    dag = DAG(
        'Reddit_dag',
        default_args=default_args,
        description='US Elections emotions dag',
        schedule_interval=timedelta(days=1),
    )
    
    run_etl = PythonOperator(
        task_id='Reddit_ETL',
        python_callable=reddit_Extraction,
        dag=dag, 
    )
    
    run_etl` 
    
    -   Save and exit the editor (press `CTRL + X`, then `Y`, and `Enter`).

## 5. Connect EC2 and S3

Your S3 bucket is already configured to receive data from your EC2 instance via the IAM role you created. When you run the ETL pipeline, the processed CSV will be automatically uploaded to S3, ensuring seamless data storage and access.

## 6. Set Up Airflow with Authentication

### Step 1: Install Airflow

1.  **Install Apache Airflow**: Follow the instructions to install Airflow in your EC2 instance:
    
    
    
    
    
    `pip install apache-airflow` 
    

### Step 2: Initialize Airflow Database

1.  **Initialize the Database**:
    
    
    
    
    
    `airflow db init` 
    

### Step 3: Create Airflow User with Password

1.  **Create a User with Authentication**: Use the following command to create a new user with a password for accessing the Airflow web interface:
    
    
    
    
    
    `airflow users create \
        --username admin \
        --firstname Admin \
        --lastname User \
        --role Admin \
        --email admin@example.com \
        --password your_password_here` 
    
    -   Replace `your_password_here` with a secure password of your choice.

### Step 4: Run Airflow on EC2

#### Step 1: Start the Airflow Scheduler

-   Open a terminal on your EC2 instance and start the Airflow scheduler:





`airflow scheduler` 

#### Step 2: Start the Airflow Webserver

-   In another terminal, start the Airflow webserver:





`airflow webserver` 

-   This will allow you to monitor your DAGs and tasks through a web interface.

### Step 3: Access the Airflow Web Interface

1.  **Open a Browser**:
    -   Go to the URL: `http://your-ec2-public-ip:8080` to access the Airflow web interface.
2.  **Log In**: Use the credentials you set up (e.g., `admin` and the password you created).
3.  **Trigger the DAG**: Click on the DAG and then click the **Trigger DAG** button to start the ETL process manually.

### Step 4: Monitor the ETL Process

-   Once the DAG is triggered, you can monitor the status of each task within the Airflow UI. The execution logs will provide insights into the success or failure of each step.

## Conclusion

You have now set up a complete ETL pipeline that extracts data from the Reddit API, performs sentiment analysis, and uploads the results to AWS S3. This pipeline can be scheduled to run daily, providing continuous updates on sentiment related to US elections.

By following this guide, you have gained experience in setting up an EC2 instance, configuring IAM roles, and utilizing Airflow for orchestrating ETL processes. Feel free to modify the pipeline as needed to suit your specific data analysis requirements or to enhance its functionality.
