import { Component } from '@angular/core';
import { SharedModule } from '../../../shared/sharedmodule';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { LoaderService } from '../../../shared/services/loader.service';
import { WorkbenchService } from '../workbench.service';
import { ToastrService } from 'ngx-toastr';
import { NgxPaginationModule } from 'ngx-pagination';
import { NgbModal, NgbModule } from '@ng-bootstrap/ng-bootstrap';
import Swal from 'sweetalert2';
import { Router } from '@angular/router';

@Component({
  selector: 'app-easy-connection',
  standalone: true,
  imports: [SharedModule, FormsModule, CommonModule, NgxPaginationModule, NgbModule],
  templateUrl: './easy-connection.component.html',
  styleUrls: ['./easy-connection.component.scss']
})
export class EasyConnectionComponent {
  serverName: string = '';
  portName: string = '';
  databaseName: string = '';
  userName: string = ''
  displayName: string = '';
  password: string = '';
  selectedSchema: string = 'public';

  selectedFile: File | null = null;

  schemaList: any[] = [];

  serverError: boolean = false;
  portError: boolean = false;
  databaseError: boolean = false;
  userNameError: boolean = false;
  displayNameError: boolean = false;
  passwordError: boolean = false;

  disableConnectBtn: boolean = true;

  toggleClass = "off-line";
  showPassword = false;
  isFormEnabled: boolean = false;

  gridView: boolean = false;
  searchConnections: string = '';
  pageSize: number = 10;
  page: number = 1;
  totalItems: number = 0;

  connectionList: any[] = [];

  showList: boolean = true;
  isEditPreview: boolean = false;
  editPreviewData: any;

  constructor(private loaderService: LoaderService, private workbenchService: WorkbenchService, private toasterservice: ToastrService,
    private modalService: NgbModal, private router: Router) {
    if (this.router.url.startsWith('/datamplify/home/easyConnection')) {
      this.showList = false;
      this.isFormEnabled = false;
    }
  }

  ngOnInit() {
    this.loaderService.hide();
    if(this.showList){
      this.getConnectionList();
    }
  }


  serverConditionError() {
    if (this.serverName) {
      this.serverError = false;
    } else {
      this.serverError = true;
    }
    this.errorCheck();
  }
  portConditionError() {
    if (this.portName) {
      this.portError = false;
    } else {
      this.portError = true;
    }
    this.serverConditionError();
    this.errorCheck();
  }
  databaseConditionError() {
    if (this.databaseName) {
      this.databaseError = false;
    } else {
      this.databaseError = true;
    }
    this.portConditionError();
    this.errorCheck();
  }
  userNameConditionError() {
    if (this.userName) {
      this.userNameError = false;
    } else {
      this.userNameError = true;
    }
    this.databaseConditionError();
    this.errorCheck();
  }
  displayNameConditionError() {
    if (this.displayName) {
      this.displayNameError = false;
    } else {
      this.displayNameError = true;
    }

    this.userNameConditionError();
    this.errorCheck();
  }
  passwordConditionError() {
    if (this.password) {
      this.passwordError = false;
    } else {
      this.passwordError = true;
    }
    this.displayNameConditionError();
    this.errorCheck();
  }
  errorCheck() {
    if (this.serverError || this.portError || this.databaseError || this.userNameError || this.displayNameError || this.passwordError) {
      this.disableConnectBtn = true;
    } else if (!(this.serverName && this.portName && this.databaseName && this.userName && this.displayName && this.password)) {
      this.disableConnectBtn = true;
    } else {
      this.disableConnectBtn = false;
    }
  }

  toggleVisibility() {
    this.showPassword = !this.showPassword;
    if (this.toggleClass === "off-line") {
      this.toggleClass = "line";
    } else {
      this.toggleClass = "off-line";
    }
  }

  openNewConnection() {
    // Centralized handler for opening the new connection form
    this.isEditPreview = false;
    this.isFormEnabled = true;
    this.showList = false;
    this.resetForm();
    console.log('New Connection: form opened');
  }

  viewConnections(){
    if (this.router.url.startsWith('/datamplify/home/easyConnection')) {
      this.router.navigate(['/datamplify/easyConnection/']); 
    } else {
      this.showList = true;
      this.getConnectionList();
    }
  }

  getSchemaList(){
    let object = {
      database_type: 1,
      hostname: this.serverName,
      port: this.portName,
      username: this.userName,
      password: this.password,
      database: this.databaseName,
      display_name: this.displayName,
    }
    console.log(object);

    this.workbenchService.getSchemaList(object).subscribe({
      next: (response) => {
        this.schemaList = response.schemas;
      },
      error: (error) => {
        this.toasterservice.error(error.error.message,'error',{ positionClass: 'toast-top-right'});
        console.error('Connection failed:', error);
      }
    });
  }

  DatabaseConnection() {
    let object = {
      database_type: 1,
      hostname: this.serverName,
      port: this.portName,
      username: this.userName,
      password: this.password,
      database: this.databaseName,
      connection_name: this.displayName,
      service_name: null,
      schema: this.selectedSchema
    }
    console.log(object);

    this.workbenchService.databaseConnection(object).subscribe({
      next: (response) => {
        this.toasterservice.success(response.message,'success',{ positionClass: 'toast-top-right'});
        console.log('Connection successful:', response);
        this.isFormEnabled = false;
        this.showList = true;
        this.resetForm();
        this.getConnectionList();
      },
      error: (error) => {
        this.toasterservice.error(error.error.message,'error',{ positionClass: 'toast-top-right'});
        console.error('Connection failed:', error);
      }
    });
  }

  updateDatabaseConnection(hierarchyId:any) {
    let object = {
      database_type: 1,
      hostname: this.serverName,
      port: this.portName,
      username: this.userName,
      password: this.password,
      database: this.databaseName,
      connection_name: this.displayName,
      service_name: null,
      schema: this.selectedSchema
    }
    console.log(object);

    this.workbenchService.updateDatabaseConnection(hierarchyId,object).subscribe({
      next: (response) => {
        this.toasterservice.success(response.message,'success',{ positionClass: 'toast-top-right'});
        console.log('Connection successful:', response);
        this.isFormEnabled = false;
        this.showList = true;
        this.resetForm();
        this.getConnectionList();
      },
      error: (error) => {
        this.toasterservice.error(error.error.message,'error',{ positionClass: 'toast-top-right'});
        console.error('Connection failed:', error);
      }
    });
  }

  editPreviewDatabaseConnection(hierarchyId: any) {
    this.workbenchService.getDatabaseConnection(hierarchyId).subscribe({
      next: (response: any) => {
        console.log(response);
        this.editPreviewData = response;
        this.serverName = response.hostname;
        this.portName = response.port;
        this.databaseName = response.database;
        this.userName = response.username;
        this.displayName = response.connection_name;
        this.password = '';
        this.selectedSchema = response.schema;
        this.isEditPreview = true;
        this.isFormEnabled = true;
        this.showList = false;
      },
      error: (err) => {
        this.toasterservice.error(err.error.message, 'error', { positionClass: 'toast-top-right' });
        console.error('Error fetching connection data:', err);
      }
    });
  }

  deleteDatabaseConnection(database:any){
    Swal.fire({
      position: "center",
      icon: "question",
      title: `Delete ${database.display_name} connection ?`,
      text: "This action cannot be undone. Are you sure you want to proceed?",
      showConfirmButton: true,
      showCancelButton: true,
      confirmButtonText: 'Yes',
      cancelButtonText: 'No',
    }).then((result) => {
      if (result.isConfirmed) {
        this.workbenchService.deleteDatabseConnection(database?.hierarchy_id).subscribe({
          next: (response: any) => {
            this.toasterservice.success(response.message,'success',{ positionClass: 'toast-top-right'});
            console.log(response);
            this.getConnectionList();
          },
          error: (err) => {
            this.toasterservice.error(err.error.message, 'error', { positionClass: 'toast-top-right' });
            console.error('Error fetching connection data:', err);
          }
        });
      }
    })
  }

  openUploadModal(content: any) {
    this.modalService.open(content, { backdrop: 'static', centered: true });
  }

  onCsvFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.selectedFile = input.files[0];
    }
    input.value = '';
  }

  fileConnection(modal: any, hierarchyId?: string) {
    if (!this.selectedFile || !this.displayName) return;

    const formData = new FormData();
    formData.append('file_path', this.selectedFile);
    formData.append('file_type', '2');
    formData.append('connection_name', this.displayName);

    const request$ = hierarchyId ? this.workbenchService.updateFileConnection(formData, hierarchyId) : this.workbenchService.fileConnection(formData);

    request$.subscribe({
      next: (response) => {
        this.toasterservice.success(response.message, 'Success', { positionClass: 'toast-top-right' });
        console.log('CSV upload successful:', response);

        modal.close();
        this.resetForm();
        this.isFormEnabled = false;
        this.showList = true;
        this.getConnectionList();
      },
      error: (error) => {
        this.toasterservice.error(error.error.message, 'Error', { positionClass: 'toast-top-right' });
        console.error('CSV upload failed:', error);
      }
    });
  }

  getFileConnection(hierarchyId: any, modal:any) {
    this.workbenchService.getFileConnection(hierarchyId).subscribe({
      next: (response: any) => {
        console.log(response);
        this.editPreviewData = response;
        this.isEditPreview = true;
        this.openUploadModal(modal);
        this.displayName = response.connection_name;
      },
      error: (err) => {
        this.toasterservice.error(err.error.message, 'error', { positionClass: 'toast-top-right' });
        console.error('Error fetching connection data:', err);
      }
    });
  }

  deleteFileConnection(database:any){
    Swal.fire({
      position: "center",
      icon: "question",
      title: `Delete ${database.display_name} connection ?`,
      text: "This action cannot be undone. Are you sure you want to proceed?",
      showConfirmButton: true,
      showCancelButton: true,
      confirmButtonText: 'Yes',
      cancelButtonText: 'No',
    }).then((result) => {
      if (result.isConfirmed) {
        this.workbenchService.deleteFileConnection(database?.hierarchy_id).subscribe({
          next: (response: any) => {
            this.toasterservice.success(response.message,'success',{ positionClass: 'toast-top-right'});
            console.log(response);
            this.getConnectionList();
          },
          error: (err) => {
            this.toasterservice.error(err.error.message, 'error', { positionClass: 'toast-top-right' });
            console.error('Error fetching connection data:', err);
          }
        });
      }
    })
  }

  getConnectionList() {
    this.workbenchService.getConnectionsList(this.page, this.pageSize, this.searchConnections).subscribe({
      next: (response: any) => {
        this.connectionList = response.data;
        this.totalItems = response.total_items ?? 10;
        console.log('Connections fetched successfully:', this.connectionList);
      },
      error: (err) => {
        this.toasterservice.error(err.error.message,'error',{ positionClass: 'toast-top-right'});
        console.error('Error fetching connections:', err);
      }
    });
  }

  resetForm() {
    this.serverName = '';
    this.portName = '';
    this.databaseName = '';
    this.userName = '';
    this.displayName = '';
    this.password = '';
    this.selectedSchema = 'public';
    this.editPreviewData = null;
    this.selectedFile = null;
    this.displayName = '';
    this.errorCheck();
  }

  onPageSizeChange() {
      const totalPages = Math.ceil(this.totalItems / this.pageSize);
      if (this.page > totalPages) {
        this.page = 1;
      }
      this.getConnectionList();
  }

  updatePagination() {
    this.totalPages = Math.max(1, Math.ceil(this.connectionList.length / this.pageSize));
    if (this.page > this.totalPages) this.page = this.totalPages;
  }

  pagedItems(): any[] {
    const start = (this.page - 1) * this.pageSize;
    return this.connectionList.slice(start, start + this.pageSize);
  }

  totalPages: number = 0;
  gotoPage(p: number) {
     this.totalPages = Math.ceil(this.totalItems / this.pageSize);
    if (p < 1 || p > this.totalPages) return;
    this.page = p;
  }

  nextPage() { if (this.page < this.totalPages) this.page++; }
  prevPage() { if (this.page > 1) this.page--; }

  editConnection(conn: any) {
    console.log('edit', conn);
    // this.editPreviewDatabaseConnection(conn.hierarchy_id);
  }

  deleteConnection(conn: any) {
    console.log('delete', conn);
    // confirm then call delete
  }

  viewConnection(conn: any) {
    console.log('view', conn);
    // open preview
  }

}
