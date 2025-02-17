# RTMS: Medical Service Web Application

![RTMS](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-333333?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![Bing API](https://img.shields.io/badge/Bing_API-008272?style=for-the-badge&logo=microsoft-bing&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)

RTMS (Real-Time Medical Services) is a web application designed to automate medical paperwork, streamline clinic location searches, and manage appointments. It significantly reduces manual workload and improves operational efficiency for medical service providers and patients.

---

## Features

- **Automated Medical Paperwork**: Reduces manual effort by automating medical documentation processes.
- **Clinic Location Search**: Utilizes Bing API for precise, location-based searches for clinics, including emergency services.
- **Appointment Management**: Facilitates seamless scheduling and management of appointments between clinics and patients.
- **Secure Database**: Built with SQLAlchemy and PostgreSQL, ensuring secure storage of sensitive data, including encrypted user passwords.
- **Medical Sharing Feature**: Enables coordination of medication delivery services, especially during the COVID-19 crisis, to minimize exposure risks.
- **REST API**: Developed with FastAPI for efficient data processing and scalable backend architecture.

---

## Technologies Used

- **Frontend**: Bootstrap, jQuery
- **Backend**: FastAPI
- **Database**: SQLAlchemy, PostgreSQL
- **APIs**: Bing API for location-based search
- **Version Control**: Git

---

## Installation

To set up the RTMS project locally, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/HopeforgeDev/RTMS.git
   cd RTMS
   ```

2. **Install Dependencies**:
   Ensure you have Python 3.8+ installed. Then, install the required packages using:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables**:
   Create a `.env` file in the root directory and add the following variables:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/rtms_db
   BING_API_KEY=your_bing_api_key
   SECRET_KEY=your_secret_key
   ```

4. **Database Setup**:
   Ensure PostgreSQL is installed and running. Create a database named `rtms_db` (or any name you prefer) and update the `DATABASE_URL` in the `.env` file accordingly.

5. **Run Migrations**:
   Apply database migrations using Alembic:
   ```bash
   alembic upgrade head
   ```

6. **Run the Application**:
   Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

7. **Access the Application**:
   Open your browser and navigate to `http://127.0.0.1:8000`.

---

## API Documentation

The RTMS API is documented using Swagger UI. After running the application, access the API documentation at:
```
http://127.0.0.1:8000/docs
```

---

## Key Contributions

- Led the development of RTMS, delivering a robust and scalable medical service web application.
- Designed and implemented an intuitive user interface using Bootstrap and jQuery.
- Integrated Bing API for precise clinic location searches, overcoming challenges in pinpointing emergency clinics.
- Built a secure and optimized REST API using FastAPI, ensuring efficient data processing and scalability.
- Developed a secure, multi-table database with SQLAlchemy and PostgreSQL, ensuring proper table relationships and data encryption.
- Implemented an appointment scheduling system to improve clinic-patient interactions.
- Collaborated with a colleague using Git for version control, ensuring smooth development and deployment.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Bing API for location-based search functionality.
- FastAPI and SQLAlchemy communities for their excellent documentation and support.

---

## Contact

For questions or feedback, feel free to reach out:
- **Email**: mhmdelhusseini45@gmail.com
- **GitHub**: [HopeforgeDev](https://github.com/HopeforgeDev)
```
