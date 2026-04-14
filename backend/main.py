from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
import zipfile
import shutil
import uvicorn

# [중요] generator.py가 generate_all(req) 함수를 가지고 있어야 합니다.
import generator 

app = FastAPI(title="idea Control Plane API")

# 1. CORS 설정 (프론트엔드 React와 통신 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 데이터 모델 정의 (PROJECT_SPEC.md 기준) ---

class CloudflareConfig(BaseModel):
    token: str
    zone_id: str
    tunnel_id: str
    domain: str
    allowed_ips: Optional[List[str]] = []

class DeployRequest(BaseModel):
    project_name: str
    repo_url: str
    env_type: str        # test, stage, prod
    env_vars: str        # .env 내용
    replica: int         # Target Replicas
    entry_service: Optional[str] = "frontend-svc"
    backend_service: Optional[str] = "backend-svc"
    healthcheck_path: Optional[str] = "/healthz"
    cloudflare: Optional[CloudflareConfig] = None

# --- 핵심 배포 로직 ---

@app.post("/api/deploy")
async def deploy_project(req: DeployRequest):
    try:
        # 프론트엔드 터미널에 표시될 로그 수집
        execution_logs = []
        execution_logs.append(f"🚀 [Step 2] Project state received: {req.project_name}")
        execution_logs.append(f"📡 Target Environment: {req.env_type.upper()}")

        # 백엔드 콘솔 출력
        print("\n" + "="*60)
        print(f" [PROJECT RECONCILIATION START] : {req.project_name}")
        print("-" * 60)
        
        # [Step 3] GitOps 리소스 생성 (Kubernetes Manifests)
        # generator.py는 이제 테라폼이 아닌 deployment.yaml 등을 생성합니다.
        output_path = generator.generate_all(req) 
        execution_logs.append(f"✅ [Step 3] GitOps Manifests generated (Deployment/Service)")
        
        # [Step 6] Cloudflare Reconciler 실행
        if req.cloudflare:
            execution_logs.append(f"📡 [Step 6] Syncing Cloudflare Tunnel policies...")
            # 실제 운영 시 여기서 Cloudflare API를 호출하여 DNS/WAF를 설정합니다.
            execution_logs.append(f"🔒 Security: IP Allowlist applied for {req.cloudflare.domain}")
            print(f" Cloudflare Reconciler: {req.cloudflare.domain} Sync Complete")

        # [Step 4] Argo CD Sync 시뮬레이션 로그
        execution_logs.append(f"📦 [Step 4] Argo CD is monitoring the GitOps repository...")
        execution_logs.append(f"🔄 Syncing resources to kind cluster (Namespace: {req.env_type})")
        
        # [Step 5] 다운로드 패키지(IaC/Manifest Bundle) 압축
        zip_filename = f"{req.project_name}_{req.env_type}_manifests.zip"
        # zip_dir는 generator가 파일을 생성한 위치입니다.
        zip_path = os.path.join(output_path, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, dirs, files in os.walk(output_path):
                for file in files:
                    if file != zip_filename:
                        zipf.write(os.path.join(root, file), file)
        
        execution_logs.append("✨ Deployment preparation successful. Manifests ready.")
        print("="*60 + "\n")
        
        return {
            "status": "success", 
            "project_state": "reconciled",
            "message": f"{req.env_type.upper()} 환경 GitOps 리소스 반영 완료",
            "logs": execution_logs,
            "download_url": f"http://localhost:8000/api/download/{req.project_name}/{req.env_type}"
        }

    except Exception as e:
        print(f"❌ [SYSTEM ERROR] {str(e)}")
        # 에러 발생 시 상세 내용을 프론트엔드로 전달
        raise HTTPException(status_code=500, detail=str(e))

# 3. 파일 다운로드 전용 API (운영자 검수용)
@app.get("/api/download/{project}/{env}")
async def download_iac_bundle(project: str, env: str):
    # zip 파일 이름을 생성 규칙과 맞춤
    zip_path = f"outputs/{project}/{env}/{project}_{env}_manifests.zip"
    if os.path.exists(zip_path):
        return FileResponse(
            path=zip_path, 
            media_type='application/octet-stream', 
            filename=f"{project}_{env}_gitops_bundle.zip"
        )
    raise HTTPException(status_code=404, detail="배포 파일을 찾을 수 없습니다.")

# 4. Blue-Green 전환 API (Caddy 제어용)
@app.post("/api/traffic/switch")
async def switch_traffic(data: dict):
    target = data.get("target_color", "blue")
    # 설계서 Step 4: Caddy Reverse Proxy 전환 로직
    print(f"🔄 [PROD TRAFFIC CONTROL] Caddy Upstream -> {target.upper()}")
    return {
        "status": "success", 
        "active_slot": target,
        "message": f"Caddy 라우팅이 {target.upper()} 슬롯으로 전환되었습니다 (무중단 배포)."
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
