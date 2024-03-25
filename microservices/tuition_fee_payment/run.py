from myapp import create_app

app = create_app()

# Port: 8001
if __name__ == '__main__':
    app.run(debug=True,port=8001)