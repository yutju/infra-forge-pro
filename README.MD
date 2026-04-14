# Infra-Forge Pro (Project IDEA)

> GitOps 기반의 온프레미스 배포 관리 플랫폼
> 운영자의 정책 선언(Declarative)만으로 인프라 프로비저닝부터 Cloudflare 네트워크 자동화까지 일관되게 실행합니다.

---

## Key Features

- Integrated Control Plane: 웹 UI를 통해 서비스 저장소, 환경 변수(.env), 복제본 수 등을 통합 관리합니다.
- IaC Automation Engine: Jinja2 템플릿과 Terraform을 결합하여 표준화된 인프라 코드를 동적으로 생성(Rendering)합니다.
- Cloudflare Reconciliation: Cloudflare API를 연동하여 Tunnel 생성 및 DNS 레코드를 자동으로 동기화합니다.
- Runtime Routing Control: 플랫폼 Caddy를 통해 / (Frontend) 및 /api (Backend) 라우팅 정책을 제어합니다.
- Environment Isolation: 개발(Dev), 스테이지(Stage), 운영(Prod) 환경별 독립적인 인프라 상태(Project State)를 유지합니다.
- Blue-Green Deployment: 운영 환경의 무중단 전환을 위한 액티브 슬롯 제어 기능을 제공합니다.

---

## System Architecture

1. User Declaration: 운영자가 UI에서 원하는 인프라 상태를 정의합니다.
2. State Modeling: Backend(FastAPI)가 요청을 수신하여 Project State 모델로 정규화합니다.
3. Template Rendering: generator.py가 Jinja2 템플릿을 사용하여 프로젝트별 Terraform 파일을 생성합니다.
4. Automated Provisioning: 생성된 코드와 Cloudflare API 호출을 통해 실제 인프라 및 네트워크 정책이 반영됩니다.

---

## Tech Stack

### Frontend
- React.js: 상태 중심의 인프라 설정 인터페이스
- Mermaid.js: 실시간 인프라 토폴로지 가시화

### Backend
- FastAPI (Python): 고성능 비동기 API 서버
- Jinja2: 동적 Terraform 템플릿 엔진
- Pydantic: 엄격한 데이터 검증 및 스키마 관리

### Infrastructure Layer
- Terraform: 클라우드/온프레미스 리소스 프로비저닝
- Cloudflare: Zero Trust 보안 터널 및 도메인 관리
- Argo CD: 선언적 GitOps 지속적 배포(CD) 관리

---

## Project Structure

```text
.
├── backend/
│   ├── templates/          # Terraform Jinja2 설계도 (VPC, EC2, RDS 등)
│   ├── outputs/            # 프로젝트별 동적 생성 IaC 결과물
│   ├── api_models.py       # Pydantic 기반 인프라 데이터 모델
│   ├── generator.py        # IaC 코드 생성 엔진 (Jinja2 기반)
│   └── main.py             # FastAPI 서버 및 Reconciler 로직
└── frontend/
    ├── src/
    │   ├── components/     # Mermaid 뷰어 등 공통 UI 컴포넌트
    │   └── App.js          # 인프라 설정 통합 인터페이스 로직
    └── package.json        # Frontend 의존성 관리





Backend Setup
Bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py


Frontend Setup
Bash
cd frontend
npm install
npm start
