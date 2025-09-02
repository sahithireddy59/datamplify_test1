import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export type SchedulerMode = 'trigger' | 'bash';

export interface SchedulerDto {
  id?: number;
  name: string;
  owner?: string;
  mode: SchedulerMode;
  schedule: string | null;
  start_date: string | null; // ISO string
  timezone: string;
  catchup: boolean;
  max_active_runs: number;
  enabled: boolean;
  target_dag_id?: string | null;
  bash_command?: string | null;
  // link to FlowBoard
  flowboard?: string | null; // UUID of FlowBoard
}

@Injectable({ providedIn: 'root' })
export class SchedulerService {
  // environment.apiUrl already includes '/v1'; DRF router exposes '/scheduler/schedulers/'
  private base = `${environment.apiUrl}/scheduler/schedulers/`;

  constructor(private http: HttpClient) {}

  list(): Observable<SchedulerDto[]> {
    return this.http.get<SchedulerDto[]>(this.base);
    // If backend uses a DRF router with pagination, adjust typing accordingly
  }

  listByFlowboard(flowboardId: string): Observable<SchedulerDto[]> {
    return this.http.get<SchedulerDto[]>(`${this.base}?flowboard=${encodeURIComponent(flowboardId)}`);
  }

  get(id: number): Observable<SchedulerDto> {
    return this.http.get<SchedulerDto>(`${this.base}${id}/`);
  }

  create(payload: SchedulerDto): Observable<SchedulerDto> {
    return this.http.post<SchedulerDto>(this.base, payload);
  }

  update(id: number, payload: Partial<SchedulerDto>): Observable<SchedulerDto> {
    return this.http.put<SchedulerDto>(`${this.base}${id}/`, payload);
  }

  delete(id: number): Observable<any> {
    return this.http.delete(`${this.base}${id}/`);
  }
}
