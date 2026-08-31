pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        disableConcurrentBuilds()
        timestamps()

        timeout(
            time: 20,
            unit: 'MINUTES'
        )
    }

    environment {
        COMPOSE_PROJECT_NAME = 'image-rag-project'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Create Environment File') {
            steps {
                withCredentials([
                    file(
                        credentialsId: 'image-rag-env',
                        variable: 'PROJECT_ENV_FILE'
                    )
                ]) {
                    sh '''
                        set +x

                        install \
                          -m 600 \
                          "$PROJECT_ENV_FILE" \
                          .env
                    '''
                }
            }
        }

        stage('Validate') {
            steps {
                sh '''
                    docker compose \
                      -f docker-compose.yaml \
                      config --quiet
                '''
            }
        }

        stage('Build') {
            steps {
                sh '''
                    docker compose \
                      -f docker-compose.yaml \
                      build --pull
                '''
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    docker compose \
                      -f docker-compose.yaml \
                      up -d \
                      --remove-orphans
                '''
            }
        }

        stage('Check Deployment') {
            steps {
                sh '''
                    docker compose \
                      -f docker-compose.yaml \
                      ps

                    for attempt in $(seq 1 15)
                    do
                        if docker exec \
                            image-rag-nginx \
                            wget \
                            --quiet \
                            --spider \
                            http://127.0.0.1/
                        then
                            echo "Nginx deployment check succeeded."
                            exit 0
                        fi

                        echo "Waiting for Nginx... (${attempt}/15)"
                        sleep 2
                    done

                    echo "Nginx deployment check failed."

                    docker logs \
                      --tail=100 \
                      image-rag-nginx

                    exit 1
                '''
            }
        }
    }

    post {
        success {
            echo 'AWS EC2 자동 배포가 완료되었습니다.'

            sh '''
                docker image prune -f
            '''
        }

        failure {
            echo 'AWS EC2 자동 배포에 실패했습니다.'

            sh '''
                docker compose \
                  -f docker-compose.yaml \
                  ps || true
            '''
        }

        always {
            sh '''
                rm -f .env
            '''
        }
    }
}