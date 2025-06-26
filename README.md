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
5. [Insights and Findings from Visualizations EDA 2024 - 01/2025](./eda_2024-01_2025.md)
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

⚙️ ETL Architecture  (updated 2025-06)

The pipeline is now 100 % **serverless-ready** and consists of two main stages
(*extract* → *transform & load*).  
Each stage will eventually run inside its own **AWS Lambda** function, but you can still execute them locally for development.


| Stage | What happens | Key AWS resources |
|-------|--------------|-------------------|
| **Extraction** | *extract.py* scrapes the Santa Lucía site with headless Chrome → saves a `.txt` per draw → uploads it **twice**:<br>  • `raw/sorteo_<N>.txt` &nbsp;(_simple bucket_)<br>  • `raw/year=<YYYY>/sorteo=<N>/…` &nbsp;(_partitioned bucket_)<br>Skips draws that are already present. | *S3 (simple + partitioned)*<br>*Secrets Manager* (bucket names)<br>*VPC Gateway Endpoint* (S3) |
| **Transformation + Load** | *transformer.py* downloads any new `.txt`, splits **HEADER / BODY**, cleans with Pandas/pyarrow, and writes:<br>  • `premios_<N>.parquet`  & `sorteos_<N>.parquet` → **simple bucket**<br>  • Hive-style `processed/premios/` & `processed/sorteos/` partitioned by `year` and `sorteo` → **partitioned bucket** | *S3 (simple + partitioned)*<br>*Secrets Manager* |
| **Discovery + Query (serverless)** | A **Glue Crawler** runs on the partitioned bucket, registers tables `loteria.premios` & `loteria.sorteos`.<br>Analysts query with **Athena** or visualise in **QuickSight** without touching the VPC. | *AWS Glue Crawler*<br>*AWS Athena*<br>*AWS QuickSight* |

---

### 🟢 Extraction phase

| Item | Details |
|------|---------|
| **Tool** | Selenium + Python |
| **Script** | [`modules/ETL/extract.py`](modules/ETL/extract.py) |
| **Flow** | 1. Open awards page → dismiss pop-up<br>2. Choose ID (or latest) → click link<br>3. Parse header/body, infer real draw number & date<br>4. Write `results_raw_lottery_id_<ID>_<title>.txt`<br>5. Upload to both buckets (simple & partitioned) |
| **Idempotence** | Before scraping, the script checks `processed/year=<YYYY>/sorteo=<N>/sorteos.parquet`; if it exists, the draw is skipped. |

---

### 🟢 Transform + Load phase

| Item | Details |
|------|---------|
| **Tool** | Pandas, PyArrow, Boto3 |
| **Script** | [`modules/ETL/transformer.py`](modules/ETL/transformer.py) |
| **Flow** | 1. List raw `.txt` files in partitioned bucket<br>2. Skip draws already processed<br>3. Download → split HEADER/BODY<br>4. Create two DataFrames:<br>   • **sorteos** (metadata + prize digits)<br>   • **premios** (ticket, letters, amount, vendor, city, depto.)<br>5. Write Parquet to **simple bucket** (`premios_<N>.parquet`, `sorteos_<N>.parquet`)<br>6. Write partitioned Parquet (`processed/premios/`, `processed/sorteos/`) to **partitioned bucket** |
| **Data model** | Columns are strongly typed; extra columns (`year`, `sorteo`) are added before partition write. |

---

### 🟢 Resulting benefits

* **Dual-bucket strategy** → quick ad-hoc analysis (simple) **and** scalable lakehouse queries (partitioned).  
* **Glue Crawler + Athena** → zero-admin SQL layer, cheap (< $5/TB scanned).  
* **QuickSight dashboards** → shareable insights without moving data out of AWS.  
* **Ready for Lambda/Step Functions** → push-button or cron-based automation.

---

> **Note:** The old `loader.py` (MySQL/RDS) has been retired to keep the stack fully serverless and cost-efficient. Historic diagrams and EDA from 2024–2025 have been moved to [`/docs/eda_2024-01_2025.md`](docs/eda_2024-2025.md).


### Conclusion

This automated ETL project demonstrates expertise in data extraction, transformation, and storage while showcasing potential for advanced analytics and visualization. It is a robust solution for managing lottery data efficiently.



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
