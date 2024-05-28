# How to Use Guide

To utilize this project effectively, follow these steps:

1. **Edit the Configuration File**: 
   - Open the config file and make necessary edits.

2. **Activate Docker Desktop**: 
   - Ensure Docker Desktop is activated and running on your system.

3. **Copy Environment Variables**: 
   - Run the following command to copy the environment variables template to the appropriate file:
     ```
     cp .envtemp .env
     ```
   - Once copied, proceed to edit the `.env` file, specifying the variables you wish to use.

4. **Build and Run Docker Compose**: 
   - Execute the following command to build and run Docker Compose:
     ```
     docker compose up --build
     ```

5. **Install Requirements**: 
   - Install any necessary requirements for your setup.

6. **Execute Prefect Script**: 
   - Finally, run the Prefect script using:
     ```
     ./prefect.sh
     ```

By following these steps, you should be able to effectively set up and utilize the system.
