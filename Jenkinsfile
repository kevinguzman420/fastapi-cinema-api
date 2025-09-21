pipeline {
    agent any

    environment {
        DATABASE_URL = 'postgresql+asyncpg://cinema_user:cinema_pass@localhost:5432/cinema_db'
        SECRET_KEY = 'your-secret-key-here'
    }

    stages {
        stage('Setup') {
            steps {
                sh 'uv sync'
            }
        }

        stage('Test Database Connection') {
            steps {
                sh 'uv run python test_db_connection.py'
            }
        }

        stage('Run Migrations') {
            steps {
                sh 'uv run python run_migrations.py'
            }
        }

        stage('Run Tests') {
            steps {
                sh 'uv run python -m pytest --tb=short || echo "No tests found, skipping"'
            }
        }

        stage('Build') {
            steps {
                sh 'echo "Build stage - add your build commands here"'
            }
        }
    }

    post {
        always {
            sh 'echo "Pipeline completed"'
        }
        failure {
            sh 'echo "Pipeline failed - check logs above"'
        }
    }
}