from src.auth.youtube_auth import run_oauth_flow


def main():
    print("Starting YouTube OAuth 2.0 setup...")
    print("A browser window will open. Sign in with your Google account.")
    print("Grant permission to upload videos to YouTube.\n")

    try:
        creds = run_oauth_flow()
        print(f"\nSuccess! Authenticated as: {creds.valid}")
        print("Refresh token has been saved to .env")
        print("You can now run the application.")
    except ValueError as e:
        print(f"\nError: {e}")
        print("Make sure YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET are set in .env")
    except Exception as e:
        print(f"\nAuthentication failed: {e}")


if __name__ == "__main__":
    main()
