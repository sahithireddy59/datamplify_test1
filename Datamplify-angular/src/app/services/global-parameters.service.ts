import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface GlobalParameter {
  id?: string;
  parameter_name: string;
  parameter_value: string;
  parameter_type: 'STRING' | 'INTEGER' | 'BOOLEAN' | 'PATH' | 'JSON';
  category: 'DIRECT_LOAD' | 'INDIRECT_LOAD' | 'GENERAL';
  description?: string;
  is_active?: boolean;
  created_at?: Date;
  updated_at?: Date;
}

export interface CSVLoadConfig {
  id?: string;
  config_name: string;
  load_type: 'DIRECT' | 'INDIRECT';
  
  // Direct Load Parameters
  batch_size?: number;
  skip_rows?: number;
  delimiter?: string;
  encoding?: string;
  quote_char?: string;
  escape_char?: string;
  
  // Indirect Load Parameters
  staging_path?: string;
  staging_table?: string;
  staging_schema?: string;
  use_bulk_insert?: boolean;
  truncate_before_load?: boolean;
  
  // Common Parameters
  header_row?: boolean;
  null_values?: string[];
  date_format?: string;
  timestamp_format?: string;
  error_handling?: 'SKIP' | 'ABORT' | 'LOG';
  max_errors?: number;
  
  // Metadata
  is_default?: boolean;
  created_at?: Date;
  updated_at?: Date;
}

@Injectable({
  providedIn: 'root'
})
export class GlobalParametersService {
  private baseUrl = environment.apiUrl;

  constructor(private http: HttpClient) { }

  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('token');
    return new HttpHeaders({
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    });
  }

  // ==================== Global Parameters ====================
  
  /**
   * Get all global parameters or filter by category
   */
  getGlobalParameters(category?: string): Observable<any> {
    const url = category 
      ? `${this.baseUrl}/connections/global_parameters/?category=${category}`
      : `${this.baseUrl}/connections/global_parameters/`;
    return this.http.get(url, { headers: this.getHeaders() });
  }

  /**
   * Create new global parameter
   */
  createGlobalParameter(parameter: GlobalParameter): Observable<any> {
    return this.http.post(
      `${this.baseUrl}/connections/global_parameters/`,
      parameter,
      { headers: this.getHeaders() }
    );
  }

  /**
   * Update existing global parameter
   */
  updateGlobalParameter(parameter: GlobalParameter): Observable<any> {
    return this.http.put(
      `${this.baseUrl}/connections/global_parameters/`,
      parameter,
      { headers: this.getHeaders() }
    );
  }

  /**
   * Delete global parameter
   */
  deleteGlobalParameter(id: string): Observable<any> {
    return this.http.delete(
      `${this.baseUrl}/connections/global_parameters/?id=${id}`,
      { headers: this.getHeaders() }
    );
  }

  // ==================== CSV Load Configuration ====================
  
  /**
   * Get all CSV load configurations or specific one
   */
  getCSVLoadConfigs(loadType?: string, id?: string): Observable<any> {
    let url = `${this.baseUrl}/connections/csv_load_config/`;
    const params: string[] = [];
    
    if (id) params.push(`id=${id}`);
    if (loadType) params.push(`load_type=${loadType}`);
    
    if (params.length > 0) {
      url += '?' + params.join('&');
    }
    
    return this.http.get(url, { headers: this.getHeaders() });
  }

  /**
   * Create new CSV load configuration
   */
  createCSVLoadConfig(config: CSVLoadConfig): Observable<any> {
    return this.http.post(
      `${this.baseUrl}/connections/csv_load_config/`,
      config,
      { headers: this.getHeaders() }
    );
  }

  /**
   * Update existing CSV load configuration
   */
  updateCSVLoadConfig(config: CSVLoadConfig): Observable<any> {
    return this.http.put(
      `${this.baseUrl}/connections/csv_load_config/`,
      config,
      { headers: this.getHeaders() }
    );
  }

  /**
   * Delete CSV load configuration
   */
  deleteCSVLoadConfig(id: string): Observable<any> {
    return this.http.delete(
      `${this.baseUrl}/connections/csv_load_config/?id=${id}`,
      { headers: this.getHeaders() }
    );
  }

  /**
   * Get default configuration for load type
   */
  getDefaultConfig(loadType: 'DIRECT' | 'INDIRECT'): Observable<any> {
    return this.http.get(
      `${this.baseUrl}/connections/default_config/?load_type=${loadType}`,
      { headers: this.getHeaders() }
    );
  }

  // ==================== Helper Methods ====================
  
  /**
   * Get default direct load configuration
   */
  getDefaultDirectLoadConfig(): CSVLoadConfig {
    return {
      config_name: 'Default Direct Load',
      load_type: 'DIRECT',
      batch_size: 1000,
      skip_rows: 0,
      delimiter: ',',
      encoding: 'utf-8',
      quote_char: '"',
      escape_char: '',
      header_row: true,
      null_values: ['', 'NULL', 'null', 'None'],
      date_format: '%Y-%m-%d',
      timestamp_format: '%Y-%m-%d %H:%M:%S',
      error_handling: 'SKIP',
      max_errors: 100,
      is_default: false
    };
  }

  /**
   * Get default indirect load configuration
   */
  getDefaultIndirectLoadConfig(): CSVLoadConfig {
    return {
      config_name: 'Default Indirect Load',
      load_type: 'INDIRECT',
      batch_size: 5000,
      skip_rows: 0,
      delimiter: ',',
      encoding: 'utf-8',
      quote_char: '"',
      escape_char: '',
      staging_path: '/tmp/staging',
      staging_table: '',
      staging_schema: 'staging',
      use_bulk_insert: true,
      truncate_before_load: false,
      header_row: true,
      null_values: ['', 'NULL', 'null', 'None'],
      date_format: '%Y-%m-%d',
      timestamp_format: '%Y-%m-%d %H:%M:%S',
      error_handling: 'SKIP',
      max_errors: 100,
      is_default: false
    };
  }

  /**
   * Validate configuration
   */
  validateConfig(config: CSVLoadConfig): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!config.config_name || config.config_name.trim() === '') {
      errors.push('Configuration name is required');
    }

    if (config.batch_size && config.batch_size < 1) {
      errors.push('Batch size must be greater than 0');
    }

    if (config.skip_rows && config.skip_rows < 0) {
      errors.push('Skip rows cannot be negative');
    }

    if (config.load_type === 'INDIRECT') {
      if (!config.staging_path || config.staging_path.trim() === '') {
        errors.push('Staging path is required for indirect load');
      }
      if (!config.staging_table || config.staging_table.trim() === '') {
        errors.push('Staging table is required for indirect load');
      }
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }
}
