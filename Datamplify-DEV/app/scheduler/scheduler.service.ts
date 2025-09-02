import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

export interface SchedulerDto {
  id?: number;
  name: string;
  owner: string;
  mode: 'trigger' | 'bash';
  target_dag_id?: string;
  bash_command?: string;
  enabled: boolean;
  schedule: string | null;
  start_date: string;     // ISO
  timezone: string;       // e.g. "Asia/Kolkata"
  catchup: boolean;
  max_active_runs: number;
}

@Injectable({ providedIn: 'root' })
export class SchedulerService {
  private base = '/api/schedulers';

  constructor(private http: HttpClient) {}

  get(id: number) {
    return this.http.get<SchedulerDto>(`${this.base}/${id}/`, { withCredentials: true });
  }

  create(body: SchedulerDto) {
    return this.http.post<SchedulerDto>(`${this.base}/`, body, { withCredentials: true });
  }

  update(id: number, body: SchedulerDto) {
    return this.http.put<SchedulerDto>(`${this.base}/${id}/`, body, { withCredentials: true });
  }
}
