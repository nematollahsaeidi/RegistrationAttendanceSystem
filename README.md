
# Video surveillance-based attendance and register 

An **Video surveillance-based attendance and register** is a digital solution designed to help companies efficiently manage and track employee attendance, work hours, and personal data. This system often integrates advanced features like biometric authentication, shift scheduling, data registration, and comprehensive reporting to streamline workforce management.  

This Flask-based application provides a robust platform for:  
1. **Attendance Management**: Query and retrieve employee attendance records based on specified time intervals.  
2. **Data Registration**: Upload and process `.zip` and video files for employee data registration.  

---
## System Overview
![diagram_image1](https://github.com/nematollahsaeidi/RegistrationAttendanceSystem/blob/main/diagram_image1.png)
## Sequence Diagram
![diagram_image2](https://github.com/nematollahsaeidi/RegistrationAttendanceSystem/blob/main/diagram_image2.PNG)

## Introduction  
This application is designed to serve companies looking for an integrated platform for:  
1. **Attendance Tracking**:  
   - Record and analyze attendance data based on user-defined timeframes.  
   - Retrieve visual proof of attendance (e.g., images captured during attendance events).  
2. **Data Upload and Processing**:  
   - Securely upload `.zip` files and video files for processing and storage.  
   - Leverage Podspace integration for robust cloud storage and retrieval.  

By automating these processes, companies can save time, reduce errors, and improve workforce management efficiency.  

---

## Installation  
1. Clone the repository:  
   ```bash  
   git clone https://github.com/nematollahsaeidi/RegistrationAttendanceSystem.git
   cd your-repo  
   ```  

2. Install dependencies:  
   ```bash  
   pip install -r requirements.txt  
   ```  

3. Ensure you have a running Elasticsearch instance for the attendance system.  

---

## Usage  

### 1. **Run the application:**  
   ```bash  
   python app.py  
   ```  
   By default, the application runs on `http://localhost:5000`.  

### 2. **Attendance System:**  
   - Navigate to `/`.  
   - Enter the following details in the form:  
     - User ID  
     - Start Time  
     - End Time  
     - Start Date  
     - End Date  
   - Submit to retrieve attendance records.  

### 3. **Data Registration System:**  
   - Navigate to `/data_register`.  
   - Upload the following:  
     - `.zip` file (optional)  
     - Video file (optional)  
   - Submit to register the files.  

---

## Endpoints  
| **Endpoint**         | **Method** | **Description**                                   |  
|-----------------------|------------|---------------------------------------------------|  
| `/`                  | `GET`      | Renders the attendance system form.              |  
| `/`                  | `POST`     | Processes attendance queries.                    |  
| `/data_register`     | `GET`      | Renders the data registration form.              |  
| `/data_register`     | `POST`     | Processes file uploads for data registration.    |  

---

## Example Queries  
### Attendance Query  
Input:  
- User ID: `12345`  
- Start Date: `2023-12-01`  
- End Date: `2023-12-02`  
- Start Time: `08:00:00`  
- End Time: `18:00:00`  

Output:  
- Attendance records with details like timestamps and images.  

### Data Registration  
Input:  
- `.zip` file: `sample_data.zip`  
- Video file: `video.mp4`  

Output:  
- Uploaded file URLs and server responses  
