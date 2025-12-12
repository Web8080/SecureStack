import axios, { AxiosInstance } from 'axios';

export interface SecureStackClientOptions {
  apiUrl: string;
  apiKey?: string;
}

export interface APITestOptions {
  endpoint: string;
  method?: string;
  headers?: Record<string, string>;
  body?: Record<string, any>;
  testTypes?: string[];
  contractSchema?: Record<string, any>;
  rateLimitThreshold?: number;
}

export interface ComplianceCheckOptions {
  framework: string;
  resourceType: string;
  resourceData: Record<string, any>;
  policyName?: string;
  customPolicy?: string;
}

export interface DependencyScanOptions {
  packageName: string;
  version?: string;
  ecosystem?: string;
}

export interface SBOMGenerateOptions {
  projectName: string;
  version: string;
  dependencies: Array<Record<string, any>>;
  format?: string;
  metadata?: Record<string, any>;
  includeAttestation?: boolean;
}

export class SecureStackClient {
  private client: AxiosInstance;

  constructor(options: SecureStackClientOptions) {
    const baseURL = `${options.apiUrl.replace(/\/$/, '')}/api/v1`;
    
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
        ...(options.apiKey && { Authorization: `Bearer ${options.apiKey}` }),
      },
    });
  }

  async testApiSecurity(options: APITestOptions): Promise<any> {
    const response = await this.client.post('/api-security/test', {
      endpoint: options.endpoint,
      method: options.method || 'GET',
      headers: options.headers,
      body: options.body,
      test_types: options.testTypes || ['contract', 'fuzzing', 'rate_limit'],
      contract_schema: options.contractSchema,
      rate_limit_threshold: options.rateLimitThreshold,
    });
    return response.data;
  }

  async getApiTests(limit = 50, offset = 0): Promise<any> {
    const response = await this.client.get('/api-security/tests', {
      params: { limit, offset },
    });
    return response.data;
  }

  async checkCompliance(options: ComplianceCheckOptions): Promise<any> {
    const response = await this.client.post('/compliance/check', {
      framework: options.framework,
      resource_type: options.resourceType,
      resource_data: options.resourceData,
      policy_name: options.policyName,
      custom_policy: options.customPolicy,
    });
    return response.data;
  }

  async getComplianceChecks(
    framework?: string,
    status?: string,
    limit = 50,
    offset = 0
  ): Promise<any> {
    const response = await this.client.get('/compliance/checks', {
      params: { framework, status, limit, offset },
    });
    return response.data;
  }

  async scanDependency(options: DependencyScanOptions): Promise<any> {
    const response = await this.client.post('/dependencies/scan', {
      package_name: options.packageName,
      version: options.version || 'latest',
      ecosystem: options.ecosystem || 'npm',
    });
    return response.data;
  }

  async scanDependenciesBatch(packages: Array<Record<string, string>>): Promise<any> {
    const response = await this.client.post('/dependencies/scan-batch', packages);
    return response.data;
  }

  async getDependencyScans(
    packageName?: string,
    minRiskScore?: number,
    limit = 50,
    offset = 0
  ): Promise<any> {
    const response = await this.client.get('/dependencies/scans', {
      params: { package_name: packageName, min_risk_score: minRiskScore, limit, offset },
    });
    return response.data;
  }

  async generateSBOM(options: SBOMGenerateOptions): Promise<any> {
    const response = await this.client.post('/sbom/generate', {
      project_name: options.projectName,
      version: options.version,
      format: options.format || 'cyclonedx',
      dependencies: options.dependencies,
      metadata: options.metadata,
      include_attestation: options.includeAttestation !== false,
    });
    return response.data;
  }

  async getSBOMDocuments(projectName?: string, limit = 50, offset = 0): Promise<any> {
    const response = await this.client.get('/sbom/documents', {
      params: { project_name: projectName, limit, offset },
    });
    return response.data;
  }

  async getSBOM(sbomId: number): Promise<any> {
    const response = await this.client.get(`/sbom/documents/${sbomId}`);
    return response.data;
  }

  async downloadSBOM(sbomId: number): Promise<ArrayBuffer> {
    const response = await this.client.get(`/sbom/documents/${sbomId}/download`, {
      responseType: 'arraybuffer',
    });
    return response.data;
  }

  async healthCheck(): Promise<any> {
    const response = await this.client.get('/health');
    return response.data;
  }
}

export default SecureStackClient;


