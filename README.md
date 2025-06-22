# End-to-End Data Pipeline for Santa Lucía Lottery: Historical Data Mining, Web Scraping, ETL, and Dynamic Visualization

## **Description:** 

In this project I tried to answer and discover insights about **"Loteria Santa Lucia de Guatemala"** which is the biggest lottery in my country (Guatemala). Also to create a historical dataset for their winnig number, due to the fact that there is no way to retrieve the old data from the past draws.

## **Table of Contents**
1. [Description](#description)
2. [Why of this project?](#why-of-this-project)
3. [Automated ETL Process for Loteria Santa Lucia Data](#automated-etl-process-for-loteria-santa-lucia-data)
   - [ETL Architecture](#etl-architecture)
   - [Extract Phase](#extract-phase)
   - [Transform Phase](#transform-phase)
   - [Load Phase](#load-phase)
   - [Results](#results)
   - [Future Steps](#future-steps)
4. [Requisites](#requisites)
5. [Insights and Findings from Visualizations](#insights-and-findings-from-visualizations-from-june012024---january052025)
   - [Prize Distribution (IQR)](#1-what-is-the-distribution-prize-of-loteria-santa-lucia-interquartile-range-🌟)
   - [Winning Numbers Distribution](#2-what-is-the-distribution-of-the-winning-numbers-of-loteria-santa-lucia-🌟)
   - [Letter Combinations Distribution](#3-what-is-the-distribution-for-the-letter-combinations-letras-of-loteria-santa-lucia)
   - [Range of Numbers for Letter Combinations](#4-so-then-what-is-the-range-of-numbers-that-get-those-letter-combinations)
   - [Luckiest Winning Numbers](#5-from-all-winning-numbers-which-one-is-the-luckiest-one-🌟)
   - [Top Sellers with Winning Numbers](#6-top-10-sellers-with-more-winning-numbers-🌟)
   - [Top Cities with Winning Numbers](#7-what-is-the-top-10-of-guatemalas-cities-with-more-winning-numbers)
   - [Top Departments with Winning Numbers](#8-what-is-the-top-10-departments-with-more-winning-numbers-sold)
   - [Departments with Most Sellers with Winning Numbers](#9-which-department-has-more-sellers-with-winning-numbers)
   - [Most Frequent Refunds](#10-what-is-the-top-5-of-the-most-frequent-refounds-reintegros)
   - [Winning Numbers Percentages](#11-from-all-numbers-sold-what-is-the-percentage-of-winning-numbers-by-lottery)
   - [Sold vs Not Sold Winning Numbers](#12-from-all-winning-numbers-ordinario-and-extraordinario-how-many-were-actually-sold)
6. [Technologies and Tools Used](#technologies-and-tools-used-🛠️)
7. [Project Structure](#project-structure)
8. [Next Steps](#next-steps)
9. [Acknowledgements](#acknowledgements)


## **Why of this project?** [Go Back ⬆️](#table-of-contents)

Lotería Santa Lucía is the largest and oldest lottery in Guatemala, founded in 1956. Unfortunately, there is no way to retrieve historical data other than through old physical newspapers, some Facebook videos (available only since 2018), or by purchasing old newspapers (PDFs) from the "National Newspaper Archive of Guatemala," which is very expensive (I tried it...).

Once a draw expires, the data is permanently erased. There is no way to perform any kind of audit on "Lotería Santa Lucía." Surprisingly, no thesis projects or university studies from Math or Statistics students have been conducted on this topic. Additionally, there is no dataset available on platforms like Kaggle.

Due to all these factors, I found a valuable way to provide data that no one else has, which could be interesting for those interested in statistics and Machine Learning.


## **Automated ETL Process for Loteria Santa Lucia Data** [Go Back ⬆️](#table-of-contents)

### Introduction

This project focuses on automating the ETL (Extract, Transform, Load) process for Santa Lucia Lottery data. The main goal is to efficiently collect, clean, and store data to enable analysis and visualization, highlighting insights such as winning patterns, frequently rewarded locations, and more.

### ETL Architecture

The ETL process consists of three primary stages:

1. **Extraction:** Retrieving raw lottery data from the web.

2. **Transformation:** Cleaning, structuring, and enriching the data.

3. **Load:** Storing the processed data into a database and locally for further use.

Below is a high-level overview of the workflow:

> [Extract raw data from the web] --> [Transform into structured datasets] --> [Load into AWS RDS]


### Extract Phase 

**Overview**

* **Tool Used:** Selenium with Python.
* **Purpose:** Scrape lottery data from the Santa Lucia lottery website.
* **Process:**

    * Open the lottery awards website.
    * Navigate to the desired draw information using a lottery ID.
    * Extract header and body data (prizes, winning numbers).
    * Save the extracted content to a .txt file for processing.

**Example**

* **Input:** Lottery number 208
* **Output:** File `results_raw_lottery_id_208.txt` stored in `./Data/raw/`

**Related Code:**

* File: `extract.py`
* Sample Function: 
    ```py
    def extract_lottery_data(lottery_number, output_folder):
        # Scrapes data and saves it to a .txt file
        pass
    ```

### Transform Phase 

**Overview**

* **Tool Used:** Pandas
* **Purpose:** Convert raw data into clean and structured datasets.
* **Process:**
    
    1. **Header Processing:**
        * Extract metadata (e.g., draw number, type, dates, main prizes, and reintegros(refounds)).

    2. **Body Processing:**
        * Extract detailed prize data, including seller information, cities, and amounts.
    
    3. **Data Cleaning:**
        * Split complex columns (e.g., `reintegros`).
        * Replace missing values.
        * Validate and format data types.

**Related Code:**

* File: `transformer.py`
* Sample Function: 

```py
def transform(folder_path, output_folder):
    # Reads raw data, cleans it, and saves structured CSVs
    pass
```

### Load Phase

**Overview**

* **Tool Used:** pymysql, AWS Secrets Manager
* **Purpose:** Upload processed data to a MySQL database hosted on AWS RDS.
* **Process:**

    1. Retrieve database credentials securely using **AWS Secrets Manager**.
    2. Establish a connection to the database.
    3. Insert data into the relevant tables (Sorteos and Premios) in batches.

**Outputs**

* Data successfully uploaded to **AWS RDS.**

**Related Code:**

* File: `loader.py`
* Sample Function:

```py
def load_csv_to_table(connection, csv_file, table_name):
    # Inserts data from CSV into a MySQL table
    pass
```

### Results

* The processed data enables:

    * Identification of patterns in winning numbers.
    * Analysis of frequently rewarded locations.
    * Visualization of trends and insights.

### Future Steps

1. Automate the ETL pipeline using **Cron Jobs** and **AWS EC2** or **AWS Lambda Functions.**
2. Implement real-time data visualization using tools like **AWS Quicksight** or **Dash.**
3. Explore predictive models to analyze patterns in winning numbers.
4. Expand automation to handle new lottery types and regions, like Mexico's National Lottery.


## Requisites [Go Back ⬆️](#table-of-contents)

* Python libraries: `selenium`, `pandas`, `pymysql`, `boto3`
* AWS setup: **RDS instance** and **Secrets Manager**.
* Tools: ChromeDriver for Selenium.

### Conclusion

This automated ETL project demonstrates expertise in data extraction, transformation, and storage while showcasing potential for advanced analytics and visualization. It is a robust solution for managing lottery data efficiently.



## Insights and Findings from Visualizations (From June/01/2024 - January/05/2025) [Go Back ⬆️](#table-of-contents)

### 1. What is the Distribution Prize of Loteria Santa Lucia? (InterQuartile Range) 🌟

* **Why Use IQR?**

    * The IQR method is robust against outliers, making it ideal for identifying anomalies in prize distributions.

    * Lottery prize data often contains extreme values (e.g., a small number of very high prizes). By focusing on the interquartile range, we can:

        * Isolate typical prize values (between the 25th and 75th percentiles).
        * Flag potential data errors or outliers for further review.

    * This method ensures a cleaner and more meaningful analysis of prize distributions.

![Distribution of money](./images/Distribution_money.png)

So with this you can see that 50% of the prizes won are **between Q600.00 and almost Q800.00**
With a **median aprox of Q750.00**

I deciced to use the IQR (InterQuartile Rule) becuase the outliers of the "big prizes" are too high above 1,000,000 up to 5,000,000 making hard to see and understand where the mayor concentration is found.


### 2. What is the distribution of the Winning Numbers of Loteria Santa Lucia? 🌟

![Distribution of money](./images/distribution_winning_numbers.png)

So, in the boxplot you can see that **50%** of winning numbers are located **between 21,000 and 62,000** aprox.
With a **median of 42,000**

When talking about winning numbers I mean a number that has won any amount of money from the range of Q500 up to Q5,000,000

### 3. What is the distribution for the Letter Combinations (letras) of Loteria Santa Lucia? 

![Distribution of money](./images/distribution_letter_combinations.png)

**What does this mean?**

50% of all letter combinations are located in: P, DT, TT, PR, PDT and C

Each letter stands for: 

**P:** Premio (Prize, won some money like Q600)

**DT:** Doble terminacion (if any of the 3 winning places finsihed with "55" any number that also finished with "55" will get some money)

**TT:** Triple Terminacion (if any of the 3 winning places finsihed with "756" any number that also finished with "756" will get some money)

**PR:** Premio y Reintegro (Prize and Refund, won some money and you get again a new ticket for next lottery)

**PDT:** Premio y Doble Terminacion (Won some money and fished with the last 2 numbers as the 1st, 2nd or 3rd place)

**C:** Centena (If the 1st, 2nd or 3thd place has a number like "55049" any number between 55000 and 55100 will get some money)

### 4. So then what is the range of numbers that get those letter combinations? 

![Distrubtion Letters by Winning numbers](./images/letters-winning-numbers-distribution.png)

**What does this mean?**

Well, It means that the numbers with the letter comination for **"p"** a mostly located between **20,000** and **60,000** e.g. if you buy a ticket number with the number 40,000 good chances are that it will get the letter "p" (of course if you get some prize in lottery) 

Same with letter combination for **DT, TT, PR, PDT and C** this just confirm again that a lot of the prizes won are between the range of numbers **20,000** and **60,000**

## 5. From all winning numbers which one is the "Luckiest" one? 🌟

## This is maybe one of the best highlights of all my findings! 🧠💥

![Top 20 luckiest winning numbers](./images/top_20_luckiest_numbers.png)

**What does this mean?**

In fact, this means that such numbers like: **13956** has won in **6 different times**, different prizes. Not necessary that won the first place but at least it won some money.

> ⚠️ IMPORTANT: Further Investigation Is Needed! 

Despite this might just `statistical noise` this might be also the `key for finding a pattern` in this data. We only have 6 months old data but as the dataset grows the chances to find (or not) a patter for  the winning numbers also increase!

## 6. Top 10 sellers with more winning numbers 🌟

## Another very important finding! 

![Top 10 sellers with winning numbers](./images/top_10_sellers_winning_numbers.png)

So Ms. **Yecenia Mazariegos** is the top seller of winning numbers, even on top of the web page "Telemarketing Loteria Santa Lucia"! 

This finding is very important, because **there is no record of the best sellers in loteria santa lucia at all**! Not even in their social networks, nothing! So, I'm the first into take a look to this very interesting insight!

Also, the cities for the top 10 sellers can be found [here](./notebooks/visualization_sorteos_premios.ipynb#top-10-sellers-location).


### 7. What is the top 10 of Guatemala's Cities with more winning numbers? 

![top 10 cities with more winning numbers](./images/top_10_cities.png)

**"De esta Capital" Means "Guatemala city"**

And as you may realize the amount of winning numbers sold in **Guatemala city is by far the largest** one in all Loteria Santa Lucia from **June 2024 up to January 5th 2025!**


Guatemala City has the largest winning numbers sold due to the huge amount of wholesellers and the web page. 

### 8. What is the top 10 departments with more winning numbers sold? 

* Guatemala is divided in the following way: 1 Country with 22 departments, 331 municipios and at least 1 or 2 "big cities" for each department. 

![Top 10 Departments with more winning numbers](./images/top_10_departments_winning.png)

At department level, **Guatemala** is still the largest one with almost 2,000 winning numbers sold, by far followed by **Quetzaltenando** and **Escuintla**.

### 9. Which department has more sellers with winning numbers? 

![Department with more sellers with winning numbers](./images/department_more_sellers.png)

At this point, Guatemala, Quetzaltenango, and Escuintla are the top three departments with sellers that have winning numbers in their records. The full list of all sellers of Lotería Santa Lucía is not available, so we can only see the sellers with winning numbers.

### 10. What is the top 5 of the most frequent refounds (reintegros)?

![top 5 of most frequent refounds](./images/top_5_general_refounds.png)

When one of the first three places ends with an "X" and the number you purchased also ends with that number (but doesn't necessarily win a larger prize), you can get a refund for the money you spent or use it to buy a new ticket.

This is the smallest prize you can win 😉


### 11. From all numbers sold, what is the percentage of winning numbers by Lottery? 

#### Extract relevant data for this calc

The lotery **'ordinario'** normaly sales up to **80,000 tickets**

The **'extraodinario'** can sale up to **90,000 tickets** (in special editions they can sale up to **100,000+** tickets).

![probabilities ordinario draws](./images/probabilities_ordinario_draws.png)

![probabilities extraordinario draws](./images/probabilities_extraodinario_draws.png)


#### This is for winning some money, not even the big prize:

So, answering the question: the percentage of winning numbers for ORDINARIOS draws is **1.09%** and for EXTRAORDINARIOS is **1.92%** 
something that basically means that in the ORDINARIO draw your chances of winning a prize is **1 in 92** meanwhile 
in an EXTRAODINARIO one the chances are **1 in 52**, so you have slightly more chances of winning some money in an 
EXTRAORDINARIO draw. 


### 12. From all winning numbers (ordinario and extraordinario), how many were actually sold? 

![winning numbers sold vs not sold](./images/winning_numbers_sold_not_sold.png)

**So what does this mean?** 

For sure the chances of getting a prize are barely minimum, on top of that, on average, 
**only the 9% of the winning number are actually sold.** this making the profit gap of 
Loteria Santa Lucia a bit better.


### At least in my investigation I saw that in 2025 Loteria Santa Lucia showed this message: 

¡Bienvenido!, de acuerdo a regulaciones de la Contraloría General de Cuentas y las regulaciones del Código Civil Decreto Ley Número 106, Artículo 2139, los sorteos se realizarán cuando se alcancen el 80% de la venta de los billetes emitidos.

Agradecemos la confianza en Lotería Santa Lucía.

**Meaning:** they are going to do the lottery only when they reach the 80% of the tickets sold. **I did not see this in 2024**


## **Technologies and Tools Used 🛠️** [Go Back ⬆️](#table-of-contents)

### Languages and Libraries 📚
- **Python:** Main language used for developing the extraction, transformation, and load (ETL) phases. 🐍
  - **Selenium:** For web automation and data extraction.
  - **Pandas:** For data cleaning, transformation, and analysis. 🐼
  - **PyMySQL:** For loading data into MySQL databases hosted on **AWS RDS**. ☁️
  - **Boto3:** To manage credentials and AWS services, including **AWS Secrets Manager.** ☁️
  - **TQDM:** For progress bar visualization during data uploads. 📈

### Cloud Services and Platforms
- **AWS RDS:** MySQL database for storing and managing processed data. ☁️
- **AWS Secrets Manager:** To securely manage credentials. ☁️
- **AWS EC2 (Future):** Server planned for automating ETL processes. 🖥️
- **AWS Lambda (Future):** Planned for real-time automation. 🖥️

### Development Environment
- **ChromeDriver:** Used by Selenium for web browser automation. 
- **Jupyter Notebooks:** For exploratory data analysis and visualization. 📔
- **GitHub:** Repository for version control and project documentation. 🐙

### Data Visualization
- **Matplotlib and Seaborn:** For creating visualizations such as distributions, boxplots, and bar charts. 🌊
- **Dash or Streamlit (Future):** For real-time data visualization.
- **AWS QuickSight (Future):** Planned for advanced visual analytics.

### Methods and Processes
- **Automated ETL:**
  - **Extraction:** Obtaining raw data from the lottery website. ✂️
  - **Transformation:** Cleaning, enriching, and structuring data using Pandas. 🦋
  - **Load:** Inserting processed data into a relational MySQL database. 📈
- **Future Automation:** Using **Cron Jobs** and serverless services to periodically execute the pipeline. ⏰


## Project Structure [Go Back ⬆️](#table-of-contents)

This project follows a modular structure to streamline the ETL process and ensure maintainability and scalability. Below is an overview of the directory and file structure:

```py
📂 Project_Root/
├── 📂 aws/                      # All files related to RDS in the cloud.
|   ├── show_tables.sql          # Example: Show all the tables and what they contain. 
├── 📂 Data/
│   ├── 📂 raw/                  # Raw data extracted directly from the lottery website.
│   │   ├── results_raw_208.txt  # Example of a raw text file containing draw data.
├── 📂 images/                   # Visualizations and plots used in analysis.
│   ├── distribution_money.png   # Example: Distribution of prize amounts.
│   ├── top_10_cities.png        # Example: Top 10 cities with most winning numbers.
├── 📂 notebooks/                # Jupyter notebooks for analysis and exploration.
│   ├── visualization_sorteos_premios.ipynb  # Contains combined visualizations and insights. ⚠️
├── 📂 modules/                  # Python modules for the ETL process.
│   ├── ETL/
│   │   ├── extract.py           # Handles data extraction using Selenium.
│   │   ├── transformer.py       # Transforms raw data into structured datasets.
│   │   ├── loader.py            # Loads cleaned data into the AWS RDS database.
├── 📃 README.md                 # Main documentation file for the project.
├── 🐍 main.py                   # Entry point to orchestrate the ETL process.
├── 🐍 download_csv.py           # download the information contained in RDS.
├── 📃 requirements.txt          # Python dependencies required for the project.
```

```
📂 Data raw/: Stores the raw text files scraped from the lottery website.
📂 images: Includes all static visualizations generated during exploratory data analysis (EDA) and for the README documentation.
📂 notebooks: Contains Jupyter notebooks used for exploring the data, generating insights, and creating visualizations.
📂 modules: 
    * ETL/: Houses scripts for each stage of the ETL pipeline:
        * extract.py: Scrapes raw lottery data using Selenium.
        * transformer.py: Cleans, processes, and structures the raw data into usable formats.
        * loader.py: Automates the upload of processed data to an AWS RDS database.
```

## **Next Steps** [Go Back ⬆️](#table-of-contents)

This project is ongoing, with several planned enhancements to fully automate the ETL pipeline and leverage cloud technologies for real-time data processing and visualization. Below are the next steps:

### 1. **Full Automation of the ETL Pipeline 🤖** 
   - **Objective:** Ensure the pipeline runs automatically without manual intervention.
   - **Implementation:**
     - Use **Cron Jobs** to schedule the ETL pipeline on an **AWS EC2 instance** or a local server.
     - Explore the use of **AWS Lambda** for serverless automation, reducing operational overhead.
     - Integrate error handling and logging mechanisms to monitor the pipeline's performance and debug issues.

### 2. **Cloud Deployment 🌩️**
   - **Objective:** Deploy the project on cloud infrastructure to ensure scalability, availability, and accessibility.
   - **Steps:**
     - Migrate processed datasets and visualizations to **AWS S3** for storage.
     - Use **AWS RDS** for managing the database and storing historical data securely.
     - Implement **AWS Secrets Manager** for managing credentials and secure database connections.

### 3. **Real-Time Data Integration ⏱️**
   - **Objective:** Update the database with the latest lottery data automatically.
   - **Features:**
     - Schedule periodic runs to fetch and process new lottery data.
     - Ensure new data is uploaded to the database without overwriting historical records.

### 4. **Real-Time Data Visualization 📊**
   - **Objective:** Provide dynamic and interactive dashboards for users to explore insights.
   - **Tools to Consider:**
     - **Streamlit or Dash:** For creating interactive dashboards.
     - **AWS QuickSight:** For advanced data analytics and visualization on the cloud.

### 5. **Enhance Data Analysis and Insights**
   - **Objective:** Identify new trends and patterns in lottery data.
   - **Ideas:**
     - Build predictive models using **machine learning** to analyze winning number patterns.
     - Expand the analysis to include correlations between prize amounts, locations, and ticket numbers.

### 6. **Documentation and Deployment 📄**
   - **Objective:** Ensure the project is well-documented for users and collaborators.
   - **Steps:**
     - Finalize and upload the project to **GitHub** with a detailed README, usage instructions, and examples.
     - Include a deployment guide for replicating the pipeline on other systems or cloud environments.

### 7. **Expand to Other Lotteries 🍀**
   - **Objective:** Apply the same framework to other lotteries in the region.
   - **Steps:**
     - Adapt the scraper to handle variations in lottery formats and data availability.
     - Create a unified database schema to integrate data from multiple sources.

## **Acknowledgements** [Go Back ⬆️](#table-of-contents)

I would like to express my gratitude to the following:

- **ChatGPT (by OpenAI):** For being an invaluable assistant throughout the development of this project, providing guidance, insights, and solutions for complex problems.
- **Loteria Santa Lucia:** For not putting any type of captcha on their website, making it easier to extract their data.
- **Family and Friends:** For their encouragement and understanding as I dedicated time and effort to this initiative.



## Documentation for partitioned datalike in S3: 

https://docs.aws.amazon.com/glue/latest/dg/incremental-crawls.html

https://docs.aws.amazon.com/glue/latest/dg/add-crawler.html

## 📌 Section: Architectural Decisions and Justification

### Separation of VPC and Serverless Services

In this project, **SageMaker Studio runs inside a private VPC** connected to S3 via a **VPC Gateway Endpoint**, which allows for local data exploration and analysis from Jupyter notebooks **without requiring internet access**.

Meanwhile, services such as **AWS Glue Crawler**, **Athena**, and **QuickSight** are configured and operate **outside the VPC**, leveraging AWS-managed network paths. This decision was made for the following reasons:

- **Simplicity in architecture**: avoids the need for VPC Interface Endpoints and additional security configuration.
- **Reduced cost**: Interface Endpoints incur hourly and per-GB charges.
- **Project context**: this is a personal project intended for demonstration purposes, not a multi-user production environment.

This separation demonstrates that a **hybrid and minimalistic architecture** can offer the best of both worlds: full technical exploration from SageMaker notebooks and effective business dashboards through QuickSight — all without incurring unnecessary operational costs.
