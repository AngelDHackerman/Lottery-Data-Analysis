## 🚧 Challenges Faced and How They Were Overcome

### 1. ❌ No Access to Historical Data
**Problem:** The official website of Lotería Santa Lucía does not preserve historical draw data. Once a draw expires, the info is gone.

**Solution:** I built a custom web scraper that extracts and stores draw data weekly. By running it frequently and storing results in AWS S3, I am building a permanent dataset from scratch — something no one else has done publicly in Guatemala.

---

### 2. 🌐 VPC Connectivity Issues
**Problem:** My initial SageMaker setup could not connect to S3 due to improper VPC endpoint configuration. SageMaker kernels would freeze or time out when accessing data.

**Solution:** After deep debugging and rebuilding the network, I implemented a correct **S3 Gateway Endpoint** in a clean VPC. This allowed SageMaker Studio to access S3 without internet or NAT, reducing latency and cost.

---

### 3. 🔄 Preventing Duplicate Work
**Problem:** I needed to avoid reprocessing draws that were already handled to save compute time and S3 storage.

**Solution:** I implemented an **idempotent check** — before scraping, the script verifies whether a processed `.parquet` file already exists in the destination bucket.

---

### 4. 💸 Cost vs Complexity Trade-offs
**Problem:** Including Athena and Glue inside the VPC required creating **Interface Endpoints**, which generate hourly and per-GB charges.

**Solution:** I documented the decision to leave Glue, Athena, and QuickSight **outside the VPC**, connecting only SageMaker via S3 Gateway Endpoint. This hybrid architecture keeps costs minimal while preserving security and scalability.