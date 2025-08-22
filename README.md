# Clash Script

## Overview
Clash Script is a Streamlit application designed to interact with the Clash of Clans API. It allows users to search for clans and players, view detailed player statistics, and manage user-selectable parameters for a customized experience.

## Project Structure
```
clash-script
├── app.py                  # Main entry point for the Streamlit application
├── parameters.py           # User-selectable variables for configuration
├── utils                   # Package containing utility functions
│   ├── __init__.py         # Empty initializer for the utils package
│   └── api.py              # Core functions for interacting with the Clash of Clans API
├── pages                   # Contains different pages for the Streamlit app
│   ├── search.py           # Search functionality for clans and players
│   └── player_details.py    # Displays detailed information about players
├── .streamlit              # Configuration settings for Streamlit
│   └── config.toml         # Theme and layout options for the app
├── requirements.txt        # Lists dependencies required for the project
└── README.md               # Documentation for the project
```

## Installation
To set up the project, clone the repository and install the required dependencies:

```bash
git clone <repository-url>
cd clash-script
pip install -r requirements.txt
```

## Usage
Run the Streamlit application using the following command:

```bash
streamlit run app.py
```

Once the application is running, you can navigate between the search and player details pages to find clans and view player statistics.

## Configuration
Adjust the user-selectable variables in `parameters.py` to customize the application settings, such as API keys and thread counts.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any suggestions or improvements.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.