pipeline {
    agent { label 'small' }
    environment {
      imagename_dev = "10.3.7.221:5000/bff-vrecli"
      imagename_staging = "10.3.7.241:5000/bff-vrecli"
      registryCredential = 'docker-registry'
      dockerImage = ''
    }

    stages {

    stage('Git clone for dev') {
        when {branch "k8s-dev"}
        steps{
          script {
          git branch: "k8s-dev",
              url: 'https://git.indocresearch.org/charite/bff_vrecli.git',
              credentialsId: 'lzhao'
            }
        }
    }
    
    stage('DEV unit test') {
      when {branch "k8s-dev"}
      steps{
          withCredentials([
            usernamePassword(credentialsId:'readonly', usernameVariable: 'PIP_USERNAME', passwordVariable: 'PIP_PASSWORD'),
            string(credentialsId:'VAULT_TOKEN', variable: 'VAULT_TOKEN'),
            string(credentialsId:'VAULT_URL', variable: 'VAULT_URL'),
            file(credentialsId:'VAULT_CRT', variable: 'VAULT_CRT')
          ]) 
        {
        sh """
        export VAULT_TOKEN=${VAULT_TOKEN}
        export VAULT_URL=${VAULT_URL}
        export VAULT_CRT=${VAULT_CRT}
        pip3 install virtualenv
        /home/indoc/.local/bin/virtualenv -p python3 venv
        . venv/bin/activate
        pip3 install -r requirements.txt -r tests/test_requirements.txt
        pytest -c tests/pytest.ini
        """
      }
    }


    stage('DEV Build and push image') {
      when {branch "k8s-dev"}
      steps{
        script {
            withCredentials([usernamePassword(credentialsId:'readonly', usernameVariable: 'PIP_USERNAME', passwordVariable: 'PIP_PASSWORD')]) {
            docker.withRegistry('http://10.3.7.221:5000', registryCredential) {
                customImage = docker.build("10.3.7.221:5000/bff-vrecli:${env.BUILD_ID}", "--build-arg pip_username=${PIP_USERNAME} --build-arg pip_password=${PIP_PASSWORD} --add-host git.indocresearch.org:10.4.3.151 .")
                customImage.push()
            }
            }
        }
      }
    }
    stage('DEV Remove image') {
      when {branch "k8s-dev"}
      steps{
        sh "docker rmi $imagename_dev:$BUILD_NUMBER"
      }
    }

    stage('DEV Deploy') {
      when {branch "k8s-dev"}
      steps{
        sh "sed -i 's/<VERSION>/${BUILD_NUMBER}/g' kubernetes/dev-deployment.yaml"
        sh "kubectl config use-context dev"
        sh "kubectl apply -f kubernetes/dev-deployment.yaml"
      }
    }

    stage('Git clone staging') {
        when {branch "k8s-staging"}
        steps{
          script {
          git branch: "k8s-staging",
              url: 'https://git.indocresearch.org/charite/bff_vrecli.git',
              credentialsId: 'lzhao'
            }
        }
    }

    stage('STAGING Building and push image') {
      when {branch "k8s-staging"}
      steps{
        script {
            withCredentials([usernamePassword(credentialsId:'readonly', usernameVariable: 'PIP_USERNAME', passwordVariable: 'PIP_PASSWORD')]) {
            docker.withRegistry('http://10.3.7.241:5000', registryCredential) {
                customImage = docker.build("10.3.7.241:5000/provenance:${env.BUILD_ID}", "--build-arg pip_username=${PIP_USERNAME} --build-arg pip_password=${PIP_PASSWORD} .")
                customImage.push()
            }
            }
        }
      }
    }

    stage('STAGING Remove image') {
      when {branch "k8s-staging"}
      steps{
        sh "docker rmi $imagename_staging:$BUILD_NUMBER"
      }
    }

    stage('STAGING Deploy') {
      when {branch "k8s-staging"}
      steps{
        sh "sed -i 's/<VERSION>/${BUILD_NUMBER}/g' kubernetes/staging-deployment.yaml"
        sh "kubectl config use-context staging"
        sh "kubectl apply -f kubernetes/staging-deployment.yaml"
      }
    }
  }
  post {
      failure {
        slackSend color: '#FF0000', message: "Build Failed! - ${env.JOB_NAME} ${env.BUILD_NUMBER}  (<${env.BUILD_URL}|Open>)", channel: 'jenkins-dev-staging-monitor'
      }
  }

}
// trigger the cicd