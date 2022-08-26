import raider

app = raider.Raider("reddit")
# Create a Raider() object for application "reddit"

app.config.proxy = "http://localhost:8080"
# Run traffic through the local web proxy

app.authenticate()
# Run authentication stages one by one

