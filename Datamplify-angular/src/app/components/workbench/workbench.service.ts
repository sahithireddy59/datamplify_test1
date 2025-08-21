import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpHeaders } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { Observable, of, throwError } from 'rxjs';
import { map, switchMap, catchError, tap } from 'rxjs/operators';
import { get } from 'lodash';
@Injectable({
  providedIn: 'root'
})
export class WorkbenchService {
  private skipLoader = false; // Flag to control the loader
  accessToken: any;
  constructor(private http: HttpClient) { }
  disableLoaderForNextRequest() {
    this.skipLoader = true;
  }

  shouldSkipLoader(): boolean {
    return this.skipLoader;
  }

  resetSkipLoader() {
    this.skipLoader = false; // Reset after request
  }

  saveThemes(obj: any) {
    return this.http.post<any>(`${environment.apiUrl}/usercustomtheme/` + this.accessToken, obj);
  }

  // API Key verification
  openApiKey(obj: any) {
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.post<any>(`${environment.apiUrl}/ai/validate-api-key/` + this.accessToken, obj);
  }

  //roles
  getSavedRolesList(obj: any) {
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.put<any>(`${environment.apiUrl}/roleslist/` + this.accessToken, obj);
  }
  getPrevilagesList(obj: any) {
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.put<any>(`${environment.apiUrl}/previlages_list/` + this.accessToken, obj);
  }
  addPrevilage(obj: any) {
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.post<any>(`${environment.apiUrl}/role/` + this.accessToken, obj);
  }
  deleteRole(id: any) {
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.delete<any>(`${environment.apiUrl}/deleterole/` + id + '/' + this.accessToken);
  }
  getRoleIdDetails(id: any) {
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.get<any>(`${environment.apiUrl}/roledetails/` + id + '/' + this.accessToken);
  }
  editRoleDetails(id: any, obj: any) {
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.put<any>(`${environment.apiUrl}/editroles/` + id + '/' + this.accessToken, obj);
  }
  //users
  getUserList(obj: any) {
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.put<any>(`${environment.apiUrl}/getusersroles/` + this.accessToken, obj);
  }
  getAddedRolesList() {
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.get<any>(`${environment.apiUrl}/roleslist/` + this.accessToken);
  }
  addUserwithRoles(obj: any) {
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.post<any>(`${environment.apiUrl}/adduser/` + this.accessToken, obj);
  }
  deleteUser(id: any) {
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.delete<any>(`${environment.apiUrl}/deleteuser/` + id + '/' + this.accessToken);
  }

  getUserIdDetails(id: any) {
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.get<any>(`${environment.apiUrl}/userdetails/` + id + '/' + this.accessToken);
  }
  editUser(id: any, obj: any) {
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.put<any>(`${environment.apiUrl}/edituser/` + id + '/' + this.accessToken, obj);
  }

  //users and roles
  getRoleDetailsDshboard() {
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.get<any>(`${environment.apiUrl}/dashboardroledetails/` + this.accessToken);
  }
  getUsersOnRole(obj: any) {
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.post<any>(`${environment.apiUrl}/multipleroles/` + this.accessToken, obj);
  }

  // easy connection
  getSchemaList(object:any){
    const currentUser = localStorage.getItem( 'currentUser' );
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.post<any>(`${environment.apiUrl}/connections/get_schema/`, object, {headers: this.buildHeaders(this.accessToken)});
  }
  databaseConnection(object: any) {
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.post<any>(`${environment.apiUrl}/connections/Database_connection/`, object, {headers: this.buildHeaders(this.accessToken)});
  }

  updateDatabaseConnection(hierarchyId: any, object: any) {
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.put<any>(`${environment.apiUrl}/connections/Database_connection/${hierarchyId}`, object, {headers: this.buildHeaders(this.accessToken)});
  }

  fileConnection(formData: FormData) {
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.post<any>(`${environment.apiUrl}/connections/File_connection/`, formData, { headers: this.buildHeaders(this.accessToken) });
  }

  updateFileConnection(formData: FormData, hierarchyId: any) {
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.put<any>(`${environment.apiUrl}/connections/File_connection/${hierarchyId}`, formData, { headers: this.buildHeaders(this.accessToken) });
  }

  getConnectionsList(page:any, pageSize:any, search:any) {
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.get<any>(`${environment.apiUrl}/connections/Connection_list/?page=${page}&page_size=${pageSize}` + (search ? `&search=${search}` : ``), { headers: this.buildHeaders(this.accessToken) });
  }

  getDatabaseConnection(hierarchyId:any){
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.get<any>(`${environment.apiUrl}/connections/Database_connection/${hierarchyId}`, { headers: this.buildHeaders(this.accessToken) });
  }

  getFileConnection(hierarchyId:any){
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.get<any>(`${environment.apiUrl}/connections/File_connection/${hierarchyId}`, { headers: this.buildHeaders(this.accessToken) });
  }

  deleteDatabseConnection(hierarchyId:any){
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.delete<any>(`${environment.apiUrl}/connections/Database_connection/${hierarchyId}`, { headers: this.buildHeaders(this.accessToken) });
  }

  deleteFileConnection(hierarchyId:any){
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.delete<any>(`${environment.apiUrl}/connections/File_connection/${hierarchyId}`, { headers: this.buildHeaders(this.accessToken) });
  }

  //etl
  saveEtl(object: any) {
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.post<any>(`${environment.apiUrl}/flowboard/flow/`, object, { headers: this.buildHeaders(this.accessToken) });
    // return this.http.post<any>(`${environment.apiUrl}/etl/` + this.accessToken, object);
  }

  updateEtl(object: any) {
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.put<any>(`${environment.apiUrl}/flowboard/flow/`, object, { headers: this.buildHeaders(this.accessToken) });
    // return this.http.put<any>(`${environment.apiUrl}/etl_update/` + this.accessToken, object);
  }

  getEtlDataFlow(id: any, type: any) {
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.get<any>(`${environment.apiUrl}/flowboard/flow/` + id, { headers: this.buildHeaders(this.accessToken) });
    // return this.http.get<any>(`${environment.apiUrl}/etl_data/` + this.accessToken + '/' + id + `?flow=${type}`);
  }

  deleteFlowboard(id: any) {
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.delete<any>(`${environment.apiUrl}/flowboard/flow/` + id, { headers: this.buildHeaders(this.accessToken) });
    // return this.http.delete<any>(`${environment.apiUrl}/dag_delete/` + this.accessToken + '/' + id);
  }

  saveTaskPlan(object: any) {
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.post<any>(`${environment.apiUrl}/taskplan/task/`, object, { headers: this.buildHeaders(this.accessToken) });
    // return this.http.post<any>(`${environment.apiUrl}/etl/` + this.accessToken, object);
  }

  updateTaskPlan(object: any) {
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.put<any>(`${environment.apiUrl}/taskplan/task/`, object, { headers: this.buildHeaders(this.accessToken) });
    // return this.http.put<any>(`${environment.apiUrl}/etl_update/` + this.accessToken, object);
  }

  getTaskPlan(id: any, type: any) {
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.get<any>(`${environment.apiUrl}/taskplan/task/` + id, { headers: this.buildHeaders(this.accessToken) });
    // return this.http.get<any>(`${environment.apiUrl}/etl_data/` + this.accessToken + '/' + id + `?flow=${type}`);
  }

  deleteTaskPlan(id: any) {
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.delete<any>(`${environment.apiUrl}/taskplan/task/` + id, { headers: this.buildHeaders(this.accessToken) });
    // return this.http.delete<any>(`${environment.apiUrl}/dag_delete/` + this.accessToken + '/' + id);
  }

  getFlowboardList(page: any, pageSize: any, search: any, type: any) {
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.get<any>(`${environment.apiUrl}/flowboard/list/` + `?page=${page}&page_size=${pageSize}` + (search ? `&search=${search}` : ``), { headers: this.buildHeaders(this.accessToken) });
    // return this.http.get<any>(`${environment.apiUrl}/dags_list/` + this.accessToken + `?page=${page}&page_size=${pageSize}` + (search ? `&search=${search}` : ``) + `&flow=${type}`);
  }

  getTaskPlanList(page: any, pageSize: any, search: any, type: any) {
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.get<any>(`${environment.apiUrl}/taskplan/list/` + `?page=${page}&page_size=${pageSize}` + (search ? `&search=${search}` : ``), { headers: this.buildHeaders(this.accessToken) });
    // return this.http.get<any>(`${environment.apiUrl}/dags_list/` + this.accessToken + `?page=${page}&page_size=${pageSize}` + (search ? `&search=${search}` : ``) + `&flow=${type}`);
  }

  runEtl(dagId: any,type:any) {
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.post<any>(`${environment.apiUrl}/monitor/Trigger/${dagId}`+`?type=${type}`, {}, { headers: this.buildHeaders(this.accessToken) });
    // return this.http.post<any>(`${environment.apiUrl}/trigger/` + dagId + '/' + this.accessToken, {});
  }

  getDataFlowStatus(object: any) {
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.post<any>(`${environment.apiUrl}/monitor/status/`, object, { headers: this.buildHeaders(this.accessToken) });
    // return this.http.post<any>(`${environment.apiUrl}/dataflow_status/` + this.accessToken, object);
  }

  getDataFlowLogs(object: any) {
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.post<any>(`${environment.apiUrl}/monitor/task_status/`, object, { headers: this.buildHeaders(this.accessToken) });
    // return this.http.post<any>(`${environment.apiUrl}/Dataflow_Task_status/` + this.accessToken, object);
  }
  getConnectionsForEtl(type: any) {
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.get<any>(`${environment.apiUrl}/connections/ETL_connection_list/` + `?type=${type}`, { headers: this.buildHeaders(this.accessToken) });
    // return this.http.get<any>(`${environment.apiUrl}/etl_source_objects/` + this.accessToken + `?connection_type=${type}`);
  }

  getTablesForDataTransformation(hierarchyId: any) {
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.get<any>(`${environment.apiUrl}/connections/Server_tables/${hierarchyId}/`, { headers: this.buildHeaders(this.accessToken) });
    // return this.http.get<any>(`${environment.apiUrl}/Database_tables/` + this.accessToken + `/${hierarchyId}`);
  }

  getDataObjectsForFile(id: any) {
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.get<any>(`${environment.apiUrl}/connections/file_schema/${id}/`, { headers: this.buildHeaders(this.accessToken) });
    // return this.http.get<any>(`${environment.apiUrl}/get_file_detials/` + this.accessToken + '/' + id);
  }
  getFilesForServer(from: any) {
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.get<any>(`${environment.apiUrl}/connections/ListFiles/?path=${from}`,{ headers: this.buildHeaders(this.accessToken) });
    // return this.http.get<any>(`${environment.apiUrl}/list-files/` + this.accessToken + `?path=${from}`);
  }
  getDataObjectsFromServer(object: any) {
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.post<any>(`${environment.apiUrl}/connections/server_files/`, object, { headers: this.buildHeaders(this.accessToken) });
    // return this.http.post<any>(`${environment.apiUrl}/server_files/` + this.accessToken, object);
  }

  // Airflow API
  airflowToken: string | null = '';
  username: string = '';

  getHeaders(): Observable<HttpHeaders> {
    const token = this.getStoredAirflowToken();
    // const token = 'eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiIsImlzcyI6W10sImF1ZCI6ImFwYWNoZS1haXJmbG93IiwibmJmIjoxNzUzODU3OTIxLCJleHAiOjE3NTM5NDQzMjEsImlhdCI6MTc1Mzg1NzkyMX0.ZkC6nv0t3xV2BQHeDhIS95Xif-NKqtGH_HsuTYBHAnDSCWQXijm5AsZkidvX6Pb7uMIN3p5aPuhg37dlSZFwOw';
    if (token) {
      return of(this.buildHeaders(token));
    } else {
      return this.getAirFlowApiToken().pipe(
        tap(res => this.storeAirflowToken(res.token)),
        map(res => this.buildHeaders(res.token))
      );
    }
  }

  private buildHeaders(token: string) {
    const headers = new HttpHeaders({
      'Accept': 'application/json',
      'Authorization': `Bearer ${token}`,
    });
    return headers;
  }


  getUserName() {
    const usernameItem = localStorage.getItem('username');
    const usernameObj = usernameItem ? JSON.parse(usernameItem ?? '') : null;
    this.username = usernameObj?.userName ?? '';
  }

  getAirFlowApiToken() {
    const currentUser = localStorage.getItem('currentUser');
    this.accessToken = JSON.parse(currentUser!)['Token'];
    return this.http.get<any>(`${environment.apiUrl}/monitor/airflow_token/`);
  }

  storeAirflowToken(token: string) {
    localStorage.setItem('airflowToken', token);
  }

  getStoredAirflowToken(): string | null {
    return localStorage.getItem('airflowToken');
  }

  clearAirflowToken() {
    localStorage.removeItem('airflowToken');
  }

  private retryWithTokenRefresh<T>(requestFn: () => Observable<T>): Observable<T> {
    return requestFn().pipe(
      catchError((error: HttpErrorResponse) => {
        if (error.status === 401) {
          return this.getAirFlowApiToken().pipe(
            switchMap(res => {
              const newToken = res.token;
              this.storeAirflowToken(newToken);
              return requestFn();
            })
          );
        }
        return throwError(() => error);
      })
    );
  }

  //monitor List
  getDags(limit: number, pageNo: number, searchTerm: string) {
    const offset = (pageNo - 1) * limit;
    this.getUserName();
    return this.getHeaders().pipe(
      switchMap(headers =>
        this.retryWithTokenRefresh(() =>
          this.http.get(`${environment.airflowApiUrl}/api/v2/dags?limit=${limit}&offset=${offset}&dag_id_pattern=${searchTerm}&tags=${this.username}&order_by=last_run_start_date`, {
            headers: headers,
          })
        )
      )
    );
  }

  //sidebar tasks runs data
  getRunAndTaskStatus(dagId: any, limit: number) {
    return this.getHeaders().pipe(
      switchMap(headers =>
        this.retryWithTokenRefresh(() =>
          this.http.get(`${environment.airflowApiUrl}/ui/grid/${dagId}?limit=${limit}&order_by=-run_after`, {
            headers: headers,
          })
        )
      )
    );
  }

  //overview header data
  getRecentDagRuns(dagId: any) {
    return this.getHeaders().pipe(
      switchMap(headers =>
        this.retryWithTokenRefresh(() =>
          this.http.get(`${environment.airflowApiUrl}/ui/dags/recent_dag_runs?dag_ids=${dagId}`, {
            headers: headers,
          })
        )
      )
    );
  }

  //dag runs data
  getDagRuns(dagId: string, limit: number, state: string, runType: string, orderBy: string) {
    return this.getHeaders().pipe(
      switchMap(headers =>
        this.retryWithTokenRefresh(() =>
          this.http.get(`${environment.airflowApiUrl}/api/v2/dags/${dagId}/dagRuns?limit=${limit}&order_by=${orderBy}` + (state ? `&state=${state}` : ``) + (runType ? `&run_type=${runType}` : ``), {
            headers: headers,
          })
        )
      )
    );
  }

  //tasks data
  getDagTasks(dagId: string) {
    return this.getHeaders().pipe(
      switchMap(headers =>
        this.retryWithTokenRefresh(() =>
          this.http.get(`${environment.airflowApiUrl}/api/v2/dags/${dagId}/tasks`, {
            headers: headers,
          })
        )
      )
    );
  }

  //task List data
  getTaskInstancesList(dagId: string, runId: string, taskId: string) {
    return this.getHeaders().pipe(
      switchMap(headers =>
        this.retryWithTokenRefresh(() =>
          this.http.get(`${environment.airflowApiUrl}/api/v2/dags/${dagId}/dagRuns/${runId}/taskInstances?task_id=${taskId}&order_by=-run_after&limit=14`, {
            headers: headers
          })
        )
      )
    );
  }

  //task runs status and duration data
  getTaskInstances(dagId: string, runId: string) {
    return this.getHeaders().pipe(
      switchMap(headers =>
        this.retryWithTokenRefresh(() =>
          this.http.get(`${environment.airflowApiUrl}/api/v2/dags/${dagId}/dagRuns/${runId}/taskInstances`, {
            headers: headers
          })
        )
      )
    );
  }

  //task and logs headers data
  getTasksHeadersData(dagId: string, runId: string) {
    return this.getHeaders().pipe(
      switchMap(headers =>
        this.retryWithTokenRefresh(() =>
          this.http.get(`${environment.airflowApiUrl}/api/v2/dags/${dagId}/dagRuns/${runId}`, {
            headers: headers
          })
        )
      )
    );
  }

  //task logs data
  getLogsOfTaskInstance(dagId: string, runId: string, taskId: string) {
    return this.getHeaders().pipe(
      switchMap(headers =>
        this.retryWithTokenRefresh(() =>
          this.http.get(`${environment.airflowApiUrl}/api/v2/dags/${dagId}/dagRuns/${runId}/taskInstances/${taskId}/logs/1?map_index=-1`, {
            headers: headers
          })
        )
      )
    );
  }
}