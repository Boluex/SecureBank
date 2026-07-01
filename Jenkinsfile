pipeline {
    agent any
    
    environment {
        BACKEND_IMAGE = 'boluex/securebank-backend'
        FRONTEND_IMAGE = 'boluex/securebank-frontend'
        DOCKERHUB_CREDENTIALS = 'dockerhub'
    }
    
    tools {
        jdk 'OpenJDK8'
    }
    
    stages {
        stage('SCM Checkout') {
            steps {
                git changelog: false, 
                    poll: false, 
                    url: 'https://github.com/Boluex/SecureBank'
            }
        }
        
        stage('Docker Build') {
            steps {
                script {
                    echo "Building Backend Docker Image..."
                    dir('backend') {
                        sh "docker build -t ${BACKEND_IMAGE}:${BUILD_NUMBER} ."
                        sh "docker tag ${BACKEND_IMAGE}:${BUILD_NUMBER} ${BACKEND_IMAGE}:latest"
                    }
                    
                    echo "Building Frontend Docker Image..."
                    dir('frontend') {
                        sh "docker build -t ${FRONTEND_IMAGE}:${BUILD_NUMBER} ."
                        sh "docker tag ${FRONTEND_IMAGE}:${BUILD_NUMBER} ${FRONTEND_IMAGE}:latest"
                    }
                }
            }
        }
        
        stage('Security Scan (Trivy)') {
            steps {
                script {
                    echo "Scanning Backend Image with Trivy..."
                    sh "trivy image --exit-code 0 --severity HIGH,CRITICAL --format table ${BACKEND_IMAGE}:${BUILD_NUMBER}"
                    
                    echo "Scanning Frontend Image with Trivy..."
                    sh "trivy image --exit-code 0 --severity HIGH,CRITICAL --format table ${FRONTEND_IMAGE}:${BUILD_NUMBER}"
                }
            }
        }
        
        stage('Docker Push') {
            steps {
                script {
                    withDockerRegistry(credentialsId: "${DOCKERHUB_CREDENTIALS}") {
                        echo "Pushing Backend Images..."
                        sh "docker push ${BACKEND_IMAGE}:${BUILD_NUMBER}"
                        sh "docker push ${BACKEND_IMAGE}:latest"
                        
                        echo "Pushing Frontend Images..."
                        sh "docker push ${FRONTEND_IMAGE}:${BUILD_NUMBER}"
                        sh "docker push ${FRONTEND_IMAGE}:latest"
                    }
                }
            }
        }
        
        stage('Trigger Manifest Update') {
            steps {
                build job: 'securebank-manifest', 
                      parameters: [
                          string(name: 'IMAGE_TAG', value: "${BUILD_NUMBER}")
                      ],
                      wait: true
            }
        }
    }
    
    post {
        always {
            echo "Cleaning up local Docker images..."
            sh "docker rmi -f ${BACKEND_IMAGE}:${BUILD_NUMBER} ${BACKEND_IMAGE}:latest || true"
            sh "docker rmi -f ${FRONTEND_IMAGE}:${BUILD_NUMBER} ${FRONTEND_IMAGE}:latest || true"
        }
        success {
            echo " Docker images pushed successfully and downstream manifest update triggered!"
        }
        failure {
            echo " Pipeline failed!"
        }
    }
}

