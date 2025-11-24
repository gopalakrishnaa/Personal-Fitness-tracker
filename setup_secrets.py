import keyring
import getpass

SERVICE_NAME = "fitness_tracker"
USERNAME = "strava_access_token"

def main():
    print("Secure Secret Setup")
    print("-------------------")
    print("This script will save your Strava Access Token to your OS's secure credential manager.")
    
    token = getpass.getpass("Enter your Strava Access Token: ")
    
    if token:
        keyring.set_password(SERVICE_NAME, USERNAME, token)
        print("\nToken saved successfully!")
        
        # Verify
        saved = keyring.get_password(SERVICE_NAME, USERNAME)
        if saved == token:
            print("Verification successful: Token can be retrieved.")
        else:
            print("Verification failed!")
    else:
        print("No token entered.")

if __name__ == "__main__":
    main()
