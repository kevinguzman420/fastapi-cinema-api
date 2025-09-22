pipeline {
    agent any
    
    environment {
        REPO_URL = 'https://github.com/kevinguzman420/fastapi-cinema-api.git'
    }
    
    stages {
        stage('Checkout') {
            when { branch 'main' }
            steps {
                echo "Branch actual: ${env.BRANCH_NAME ?: 'desconocida'}"
                echo 'Cloning/Pulling latest code from GitHub (solo main)...'
                git branch: 'main', url: env.REPO_URL
            }
        }

        stage('Setup uv') {
            when { branch 'main' }
            steps {
                echo 'Installing uv package manager...'
                sh '''
                    if ! command -v uv &> /dev/null; then
                        echo "Installing uv..."
                        curl -LsSf https://astral.sh/uv/install.sh | sh
                    fi

                    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
                    uv --version
                '''
            }
        }

        stage('Install Dependencies') {
            when { branch 'main' }
            steps {
                echo 'Installing dependencies with uv...'
                sh '''
                    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
                    uv sync
                '''
            }
        }

        stage('Setup Production Config') {
            when { branch 'main' }
            steps {
                echo 'Setting up production configuration...'
                sh '''
                    # Use production alembic config
                    cp alembic.production.ini alembic.ini
                    echo "Production alembic.ini configured"
                '''
            }
        }

        stage('Database Migration') {
            when { branch 'main' }
            steps {
                echo 'Running database migrations...'
                sh '''
                    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

                    echo "Running migrations..."
                    uv run alembic upgrade head
                '''
            }
        }

        stage('Deploy') {
            when { branch 'main' }
            steps {
                echo 'Deploying FastAPI Cinema API...'
                sh '''
            export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

            # Kill previous instance
            pkill -f "uvicorn main:app" || true
            sleep 2

            # Start new instance (FIXED)
            nohup uv run uvicorn main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &

            # Wait for startup
            sleep 5
            echo "FastAPI Cinema API deployed on port 8000"

            # Check if the service is running
            if pgrep -f "uvicorn main:app" > /dev/null; then
                echo "✅ Service is running successfully"
                # Optional: Test the endpoint
                curl -f http://localhost:8000/ || echo "⚠️  App started but endpoint not responding yet"
            else
                echo "❌ Service failed to start"
                echo "Checking logs:"
                cat app.log || echo "No log file found"
                exit 1
            fi
        '''
            }
        }
    }
    
    post {
        success {
            echo '✅ Deployment completed successfully!'
        }
        failure {
            echo '❌ Deployment failed. Check logs for details.'
        }
    }
}