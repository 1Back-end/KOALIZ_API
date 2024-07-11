pipeline {
    agent any
    options {
        skipStagesAfterUnstable()
    }
    stages {
        stage('Clone repository') {
            steps {
                script{
                    sh 'printenv'
                    echo 'Pulling...' + env.BRANCH_NAME
                    checkout scm
                }
            }
        }

        stage('Build') {
            steps {
                script{
                    slackSend(message: "${env.JOB_NAME} #${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)\nBuild commencé", channel: "bde-micro-creche")
                    if (env.BRANCH_NAME == 'master') {
                        app = docker.build("registry.gitlab.com/kevmaxsarl/mc-app/api:latest")
                    } else {
                        app = docker.build("registry.gitlab.com/kevmaxsarl/mc-app/api:"+env.BRANCH_NAME)
                    }
                }
            }
        }
        stage('Test'){
            steps {
                echo 'Empty...'
            }
        }
        stage('Deploy') {
            steps {
                script{
                    docker.withRegistry('https://registry.gitlab.com/kevmaxsarl/mc-app/api', 'gitlab_username_password') {
                        //app.push("${env.BUILD_NUMBER}")
                        if (env.BRANCH_NAME == 'master') {
                            app.push("latest")
                        } else {
                            app.push(env.BRANCH_NAME)
                        }
                    }
                }
            }
        }
    }
    
    post {
        success {
            slackSend(color: "good", message: "${env.JOB_NAME} ${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)\nBuild effectué avec succès", channel: "bde-micro-creche")
        }
        failure {
            slackSend(failOnError:true, message:"${env.JOB_NAME} ${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)\nÉchec de build", channel: "bde-micro-creche")
        }
    }

}
