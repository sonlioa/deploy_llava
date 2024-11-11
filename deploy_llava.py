import os
import subprocess

# Docker 和 Kubernetes 配置
IMAGE_NAME = "llava-image:latest"
DEPLOYMENT_NAME = "llava-deployment"
NAMESPACE = "default"
APP_ID = "llava-service"

# Dockerfile 內容
DOCKERFILE_CONTENT = '''
# 使用支持 CUDA 的基礎映像，例如 NVIDIA 提供的 PyTorch 映像
FROM pytorch/pytorch:latest

# 安裝基礎依賴
RUN apt-get update && apt-get install -y git curl && \\
    pip install --upgrade pip

# Clone LLaVA 的代碼庫
RUN git clone https://github.com/haotian-liu/LLaVA.git /LLaVA
WORKDIR /LLaVA

# 安裝 LLaVA 所需的依賴
COPY requirements.txt /LLaVA/requirements.txt
RUN pip install -r requirements.txt

# 安裝 Hugging Face Transformers 和 Diffusers
RUN pip install transformers diffusers

# 啟動 API 服務
COPY serve.py /LLaVA/serve.py
CMD ["python", "serve.py"]
'''

# Kubernetes Deployment 配置
K8S_DEPLOYMENT_YAML = f'''
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {DEPLOYMENT_NAME}
  namespace: {NAMESPACE}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: llava
  template:
    metadata:
      labels:
        app: llava
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "{APP_ID}"
        dapr.io/app-port: "5000"
    spec:
      containers:
        - name: llava-container
          image: {IMAGE_NAME}
          ports:
            - containerPort: 5000
          resources:
            limits:
              nvidia.com/gpu: 1  # 若需要 GPU 加速
'''

def write_file(filename, content):
    """Write content to a file."""
    with open(filename, 'w') as f:
        f.write(content)

def build_docker_image():
    """Build the Docker image for LLaVA."""
    # 寫入 Dockerfile
    write_file("Dockerfile", DOCKERFILE_CONTENT)
    # 構建 Docker 映像
    print("Building Docker image...")
    subprocess.run(["docker", "build", "-t", IMAGE_NAME, "."], check=True)

def create_k8s_deployment():
    """Deploy the LLaVA image as a pod on Kubernetes with Dapr."""
    # 寫入 Kubernetes YAML 文件
    write_file("llava-deployment.yaml", K8S_DEPLOYMENT_YAML)
    # 應用 Kubernetes 配置
    print("Creating Kubernetes deployment...")
    subprocess.run(["kubectl", "apply", "-f", "llava-deployment.yaml"], check=True)

def main():
    """Main function to build and deploy LLaVA with Dapr."""
    # 檢查 Docker 和 Kubernetes 狀態
    try:
        subprocess.run(["docker", "--version"], check=True)
        subprocess.run(["kubectl", "version", "--client"], check=True)
        subprocess.run(["dapr", "--version"], check=True)
    except subprocess.CalledProcessError:
        print("請確保已安裝 Docker, Kubernetes, 和 Dapr CLI。")
        return

    # 構建並部署 LLaVA
    build_docker_image()
    create_k8s_deployment()
    print(f"LLaVA 部署成功，使用 Dapr 應用 ID: {APP_ID}")

if __name__ == "__main__":
    main()

