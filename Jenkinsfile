pipeline {
    agent { label 'small' }
    environment {
      imagename_dev = "ghcr.io/pilotdataplatform/bff_cli"
      imagename_staging = "ghcr.io/pilotdataplatform/bff_cli"
      commit = sh(returnStdout: true, script: 'git describe --always').trim()
      registryCredential = 'pilot-ghcr'
      registryURL = "https://github.com/PilotDataPlatform/bff-cli.git"
      registryURLBase = "https://ghcr.io"
      dockerImage = ''
    }

    stages {

    stage('Git clone for dev') {
        when {branch "develop"}
        steps{
          script {
          git branch: "develop",
              url: "$registryURL",
              credentialsId: 'lzhao'
            }
        }
    }
/**
    stage('DEV unit test') {
      when {branch "develop"}
      steps{
          withCredentials([
            usernamePassword(credentialsId:'readonly', usernameVariable: 'PIP_USERNAME', passwordVariable: 'PIP_PASSWORD'),
            string(credentialsId:'VAULT_TOKEN', variable: 'VAULT_TOKEN'),
            string(credentialsId:'VAULT_URL', variable: 'VAULT_URL'),
            file(credentialsId:'VAULT_CRT', variable: 'VAULT_CRT')
          ])
          {
            sh """
            export CONFIG_CENTER_ENABLED='true'
            export VAULT_TOKEN=${VAULT_TOKEN}
            export VAULT_URL=${VAULT_URL}
            export VAULT_CRT=${VAULT_CRT}
            pip3 install virtualenv
            /home/indoc/.local/bin/virtualenv -p python3.8 venv
            . venv/bin/activate
            PIP_USERNAME=${PIP_USERNAME} PIP_PASSWORD=${PIP_PASSWORD} pip3 install -r requirements.txt -r internal_requirements.txt -r tests/test_requirements.txt
            pip freeze | grep logger
            pytest -c tests/pytest.ini
            """
            }
      }
    }
**/
    stage('DEV Build and push image') {
      when {branch "develop"}
      steps{
        script {
            withCredentials([usernamePassword(credentialsId:'readonly', usernameVariable: 'PIP_USERNAME', passwordVariable: 'PIP_PASSWORD')]) {
            docker.withRegistry("$registryURLBase", registryCredential) {
                customImage = docker.build("$imagename_dev:$commit", "--build-arg pip_username=${PIP_USERNAME} --build-arg pip_password=${PIP_PASSWORD} .")
                customImage.push()
            }
            }
        }
      }
    }
    stage('DEV Remove image') {
      when {branch "develop"}
      steps{
        sh "docker rmi $imagename_dev:$commit"
      }
    }

    stage('DEV Deploy') {
      when {branch "develop"}
      steps{
        build(job: "/VRE-IaC/UpdateAppVersion", parameters: [
          [$class: 'StringParameterValue', name: 'TF_TARGET_ENV', value: 'dev' ],
          [$class: 'StringParameterValue', name: 'TARGET_RELEASE', value: 'bff-vrecli' ],
          [$class: 'StringParameterValue', name: 'NEW_APP_VERSION', value: "$commit" ]
        ])
      }
    }
/**
    stage('Git clone staging') {
        when {branch "main"}
        steps{
          script {
          git branch: "main",
              url: "registryURL",
              credentialsId: 'lzhao'
            }
        }
    }

    stage('STAGING Building and push image') {
      when {branch "main"}
      steps{
        script {
            withCredentials([usernamePassword(credentialsId:'readonly', usernameVariable: 'PIP_USERNAME', passwordVariable: 'PIP_PASSWORD')]) {
            docker.withRegistry("$registryURLBase", registryCredential) {
                customImage = docker.build("$imagename_staging:$commit", "--build-arg pip_username=${PIP_USERNAME} --build-arg pip_password=${PIP_PASSWORD} .")
                customImage.push()
            }
            }
        }
      }
    }

    stage('STAGING Remove image') {
      when {branch "main"}
      steps{
        sh "docker rmi $imagename_staging:$commit"
      }
    }

    stage('STAGING Deploy') {
      when {branch "main"}
      steps{
        build(job: "/VRE-IaC/Staging-UpdateAppVersion", parameters: [
            [$class: 'StringParameterValue', name: 'TF_TARGET_ENV', value: 'staging' ],
            [$class: 'StringParameterValue', name: 'TARGET_RELEASE', value: 'bff-vrecli' ],
            [$class: 'StringParameterValue', name: 'NEW_APP_VERSION', value: "$commit" ]
        ])
      }
    }
**/    
  }
  post {
      failure {
        slackSend color: '#FF0000', message: "Build Failed! - ${env.JOB_NAME} $commit  (<${env.BUILD_URL}|Open>)", channel: 'jenkins-dev-staging-monitor'
      }
  }

}
