import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface FlowboardListItem {
  id: string;
  Flow_id: string;
  Flow_name: string;
  DrawFlow: any;
  user_id: string | null;
  parsed: boolean;
  has_scheduler?: boolean;
}

export interface FlowboardListResponse {
  data: FlowboardListItem[];
  total_pages: number;
  total_records: number;
  page_number: number;
  page_size: number;
}

@Injectable({ providedIn: 'root' })
export class FlowboardService {
  private base = `${environment.apiUrl}/flowboard/flow/`;

  constructor(private http: HttpClient) {}

  list(opts?: { search?: string; page?: number; page_size?: number }): Observable<FlowboardListResponse> {
    let params = new HttpParams();
    if (opts?.search) params = params.set('search', opts.search);
    if (opts?.page) params = params.set('page', String(opts.page));
    if (opts?.page_size) params = params.set('page_size', String(opts.page_size));
    return this.http.get<FlowboardListResponse>(this.base, { params });
  }
}
