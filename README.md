# Coraline Data Engineering Challenge

โปรเจกต์ ETL ที่ทำหน้าที่:

1. **โหลด (Load)** ข้อมูลทุกปีจากชีต `FoodSales` ในไฟล์ `de_challenge_data.xlsx` เข้า
   ตาราง `food_sales` บน PostgreSQL (เขียนด้วย Python)
2. **สร้าง (Build)** ตาราง pivot `cat_reg` (ยอดขายรวมตาม Category แยกตาม Region) จาก
   `food_sales` (เขียนด้วย SQL)
3. **จัดคิวงานและตั้งเวลารัน** ด้วย Apache Airflow โดยทั้งหมดรันผ่าน **Docker Compose** (Postgres + Airflow)

## สถาปัตยกรรม

```
de_challenge_data.xlsx
        │
        │  src/extract.py  (หา block ของแต่ละปีอัตโนมัติแล้วรวมเข้าด้วยกัน)
        ▼
   pandas DataFrame  ──ทำความสะอาดและกำหนด type──┐
        │                                          │
        │  src/load.py                            │
        ▼                                          │
┌───────────────────┐                              │
│ Postgres:          │◄──────────────────────────────┘
│ food_sales table    │
└─────────┬───────────┘
          │  sql/create_cat_reg.sql (รันผ่าน src/sql_runner.py)
          ▼
┌───────────────────┐
│ Postgres:          │
│ cat_reg table       │
└────────────────────┘

จัดคิวงานด้วย dags/food_sales_etl_dag.py (Airflow, @daily):
   extract_and_load_food_sales  >>  build_cat_reg
```

ทั้งหมดนี้รันอยู่ภายใน Docker Compose (Postgres 16 + Airflow 2.9)

## โครงสร้างโปรเจกต์

```
.
├── config/config.yaml           # ค่า config ที่ไม่ใช่ความลับ (path, ชื่อตาราง, schedule)
├── .env.example                 # ต้นแบบไฟล์ config ที่เป็นความลับ (ค่า default ตรงสเปคโจทย์อยู่แล้ว)
├── src/
│   ├── config.py                # โหลด config.yaml + env var มาเป็น Settings ที่มี type
│   ├── extract.py                # Excel -> DataFrame (จัดการ block ของแต่ละปีที่ซ้อนกัน)
│   ├── load.py                   # DataFrame -> Postgres (โหมด replace / upsert)
│   ├── db.py                     # SQLAlchemy engine + DDL ของ food_sales
│   ├── sql_runner.py             # รันไฟล์ .sql เป็น transaction เดียว
│   ├── etl.py                    # ฟังก์ชัน task ที่ Airflow DAG เรียกใช้
│   └── logger.py                 # ตั้งค่า logging กลาง
├── sql/create_cat_reg.sql       # ข้อ 2 ของโจทย์: สร้าง cat_reg จาก food_sales
├── dags/food_sales_etl_dag.py   # Airflow DAG: orchestration + schedule
├── postgres-init/                # init script ของ Postgres (สร้าง database airflow_meta)
├── docker-compose.yml           # Postgres + Airflow ครบในคำสั่งเดียว
├── tests/test_extract.py        # unit test ของส่วนที่ซับซ้อนที่สุดของ pipeline
└── data/de_challenge_data.xlsx  # ไฟล์ข้อมูลต้นทาง
```

## วิธีรันโปรเจกต์ (Docker)

รันด้วย Docker Compose เท่านั้น (Postgres + Airflow มาในชุดเดียว) ตามขั้นตอนที่ทดสอบจริง
มีดังนี้:

### 1. เตรียมโปรเจกต์และไฟล์ตั้งค่า

แตกไฟล์โปรเจกต์ แล้ว copy ไฟล์ตัวอย่างเป็น `.env` จริง (ค่า default ตรงสเปคโจทย์อยู่แล้ว
คือ database `challenge`, user `root`, password `DataEngineer_2024` — ไม่ต้องแก้ก็รันได้ทันที):

```bash
cd coraline-de-challenge
cp .env.example .env
```

### 2. สั่งรัน Postgres + Airflow

```bash
docker compose up -d
docker compose ps
```

คำสั่งนี้จะดึง image ของ Postgres 16 และ Airflow 2.9 มารัน พร้อม mount โค้ดของโปรเจกต์
เข้า container ของ Airflow ให้อัตโนมัติ (รอบแรกจะช้าหน่อยเพราะต้องโหลด image และติดตั้ง
python package) หลังรันคำสั่งที่สองแล้ว ทั้งสอง service (`coraline_postgres`,
`coraline_airflow`) ควรขึ้นสถานะ `Up` หรือ `healthy`

> **หมายเหตุ (ปัญหาที่เคยเจอระหว่างทดสอบ):** รอบแรกที่รัน Airflow อาจขึ้น error
> `AirflowConfigException: cannot use SQLite with the LocalExecutor` เพราะ
> `LocalExecutor` ต้องใช้ฐานข้อมูลจริงเก็บ metadata ของตัวเอง จึงแก้โดยให้ Postgres
> สร้าง database แยกชื่อ `airflow_meta` ขึ้นมาอีกอันสำหรับเก็บ metadata ของ Airflow
> (แยกจาก database `challenge` ที่เก็บข้อมูลจริงของโจทย์) ผ่านไฟล์
> `postgres-init/01-create-airflow-db.sql`
>
> **สำคัญ:** ไฟล์ init script ของ Postgres จะรันแค่ตอนที่ volume ว่างเปล่าเท่านั้น
> ถ้าเคยรัน `docker compose up` มาก่อนแล้วเจอ error นี้ ต้องล้าง container และ volume
> เก่าทิ้งก่อน ไม่งั้น database `airflow_meta` จะไม่ถูกสร้างและ error เดิมจะกลับมาอีก:
>
> ```bash
> docker compose down -v
> docker compose ps
> docker volume ls
> docker volume rm coraline-de-challenge_postgres_data   # ถ้ายังเห็น volume เดิมค้างอยู่
> docker compose up -d
> ```

### 3. หา password เข้าใช้งาน Airflow UI

Airflow standalone จะสุ่ม password ของ user `admin` ให้อัตโนมัติตอนสร้าง container
ครั้งแรก และเขียนเก็บไว้ในไฟล์ข้างใน container วิธีที่แม่นที่สุดคือดึงไฟล์นั้นออกมาอ่านตรง ๆ:

```bash
docker exec -it coraline_airflow cat /opt/airflow/standalone_admin_password.txt
```

(บน PowerShell ใช้ `Select-String` แทน `grep` ได้ เช่น
`docker compose logs airflow | Select-String -Pattern "Login with"` — แต่การอ่านไฟล์
ตรง ๆ ด้านบนแม่นยำและเร็วกว่า)

### 4. Login และ Trigger DAG

1. เปิดเบราว์เซอร์ไปที่ `http://localhost:8080`
2. Login ด้วย username `admin` และ password ที่ได้จากขั้นตอนที่ 3
3. จะเห็น DAG ชื่อ `food_sales_etl` ในหน้ารายการ — กดปุ่ม **Trigger DAG** (ไอคอนรูปสามเหลี่ยม)
   เพื่อรันทันที
4. รอดูจนทั้ง 2 task ขึ้นสีเขียว: `extract_and_load_food_sales` → `build_cat_reg`

ถ้า task ขึ้นสีแดง (fail) ให้คลิกเข้าไปที่กล่อง task แล้วกด **Logs** เพื่อดู error เต็ม ๆ

### 5. ตรวจสอบผลลัพธ์ในฐานข้อมูล

เช็คจำนวนแถวในตาราง `food_sales` (ต้องรวมข้อมูลทั้งปี 2022 และ 2023):

```bash
docker exec -it coraline_postgres psql -U root -d challenge -c "SELECT COUNT(*) FROM food_sales;"
```

เช็คตาราง `cat_reg` (pivot ยอดขายตาม Category และ Region):

```bash
docker exec -it coraline_postgres psql -U root -d challenge -c "SELECT * FROM cat_reg ORDER BY category;"
```

### 6. ทดสอบความ idempotent (รันซ้ำต้องไม่พัง)

กลับไป trigger DAG `food_sales_etl` ซ้ำอีกรอบใน Airflow UI แล้วเช็คจำนวนแถวใน
`food_sales` อีกครั้ง — ต้องยังคงได้ 244 เท่าเดิม (ไม่ขึ้นเป็น 488 และไม่มี error) เพราะ
`food_sales` ใช้กลยุทธ์ `TRUNCATE` + reload และ `cat_reg` ใช้ `DROP` + `CREATE` ใหม่ทุกครั้ง
ทำให้ปลอดภัยเวลารันซ้ำ, retry, หรือ backfill ตรงตามเกณฑ์ "ปฏิบัติงานได้โดยไม่เกิดข้อผิดพลาด"
ของโจทย์

### รันเทสต์

```bash
pip install pytest
python -m pytest tests/ -v
```

## การตรวจสอบผลลัพธ์

รันโปรเจกต์กับไฟล์ `de_challenge_data.xlsx` ที่ให้มา จะได้ผลลัพธ์ดังนี้:

- `food_sales`: **244 แถว** ครอบคลุมตั้งแต่ 2022-01-01 ถึง 2023-12-30 (รวมข้อมูลทั้งสองปีไว้ในตารางเดียว)
- `cat_reg`:

  | category | east     | west    | grand_total |
  |----------|----------|---------|-------------|
  | Bars     | 6355     | 4180    | 10536       |
  | Cookies  | 10684    | 6529    | 17212       |
  | Crackers | 3026     | 314     | 3340        |
  | Snacks   | 1460     | 778     | 2238        |

การ trigger DAG ซ้ำ (หรือรันซ้ำหลาย ๆ รอบ) ให้ผลลัพธ์เหมือนเดิมทุกครั้ง — ไม่มีข้อมูลซ้ำและไม่มี error

## Config reference

| ค่า config                             | อยู่ที่ไฟล์                                          | ค่า default                             | หน้าที่                                            |
| `POSTGRES_HOST/PORT/DB/USER/PASSWORD` | `.env`                                           | `challenge`/`root`/`DataEngineer_2024` | ใช้เชื่อมต่อฐานข้อมูล                                |
| `excel.file_path`                     | `config/config.yaml` หรือ `EXCEL_FILE_PATH`       | `data/de_challenge_data.xlsx`          | path ของไฟล์ข้อมูลต้นทาง                          |
| `etl.load_strategy`                   | `config/config.yaml` หรือ `ETL_LOAD_STRATEGY`     | `replace`                              | `replace` (full refresh) หรือ `append` (upsert) |
| Airflow DAG schedule                  | `dags/food_sales_etl_dag.py` `schedule_interval` | `@daily`                               | เปลี่ยน schedule ได้โดยไม่ต้องแก้ logic ของ pipeline |