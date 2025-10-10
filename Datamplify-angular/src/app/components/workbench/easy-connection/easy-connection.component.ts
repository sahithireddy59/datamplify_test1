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
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';

@Component({
  selector: 'app-easy-connection',
  standalone: true,
  imports: [SharedModule, FormsModule, CommonModule, NgxPaginationModule, NgbModule],
  templateUrl: './easy-connection.component.html',
  styleUrl: './easy-connection.component.scss'
})
export class EasyConnectionComponent {
  // Common fields
  serverName: string = '';
  portName: string = '';
  databaseName: string = '';
  userName: string = ''
  displayName: string = '';
  password: string = '';
  selectedSchema: string = 'public';
  selectedFile: File | null = null;
  schemaList: any[] = [];
  
  // Oracle specific
  serviceName: string = '';
  
  // SQLite/Access specific
  databasePath: string = '';
  
  // MongoDB specific
  connectionString: string = '';
  authDatabase: string = '';
  
  // Snowflake specific
  account: string = '';
  warehouse: string = '';
  role: string = '';
  
  // Cassandra specific
  keyspace: string = '';
  
  // CSV dynamic path fields
  csvSourceType: string = 'upload'; // 'upload' or 'dynamic'
  dynamicFilePath: string = '';
  fileNameParameter: string = '';
  
  // File server details for dynamic path
  fileServerType: string = 'local'; // 'local', 'ftp', 'sftp', 's3', 'azure', 'network'
  fileServerHost: string = '';
  fileServerPort: string = '';
  fileServerProtocol: string = 'passive'; // 'active' or 'passive'
  fileServerUsername: string = '';
  fileServerPassword: string = '';
  showFileServerPassword: boolean = false;
  fileServerAuthType: string = 'password'; // 'password' or 'file'
  selectedAuthFile: File | null = null;
  serverError: boolean = false;
  portError: boolean = false;
  databaseError: boolean = false;
  userNameError: boolean = false;
  displayNameError: boolean = false;
  passwordError: boolean = false;
  disableConnectBtn: boolean = true;
  toggleClass = "off-line";
  showPassword = false;
  gridView: boolean = true;
  searchConnections: string = '';
  pageSize: number = 9;
  page: number = 1;
  totalItems: number = 0;
  connectionList: any[] = [];
  showList: boolean = true;
  isEditPreview: boolean = false;
  editPreviewData: any;
  isLoading: boolean = false;
  selectedCategory: string | null = null;
  selectedConnectionType: string | null = null;
  showRelational = false;
  showNoSQL = false;
  showCloudWarehouse = false;
  showEnterprise = false;
  showFiles = false;
  viewNewConnection = false;
  selectedConnection: string | null = null;
  existingConnections: any = [];
  skeletons = Array(9);

  constructor(private loaderService: LoaderService, private workbenchService: WorkbenchService, private toasterservice: ToastrService,
    private modalService: NgbModal, private router: Router,private sanitizer: DomSanitizer) {
    if (this.router.url.startsWith('/datamplify/easyConnection/newConnection')) {
      this.showList = false;
      this.viewNewConnection = true;
    }
  }

  ngOnInit() {
    this.loaderService.hide();
    if(this.showList){
      this.getConnectionList();
    }
  }

  displayNameConditionError() {
    if (this.displayName) {
      this.displayNameError = false;
    } else {
      this.displayNameError = true;
    }

    this.errorCheck();
  }
  serverConditionError() {
    if (this.serverName) {
      this.serverError = false;
    } else {
      this.serverError = true;
    }

    this.displayNameConditionError();
    this.errorCheck();
  }
  portConditionError() {
    if (this.portName) {
      this.portError = false;
    } else {
      this.portError = true;
    }
    this.serverConditionError()
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
  passwordConditionError() {
    if (this.password) {
      this.passwordError = false;
    } else {
      this.passwordError = true;
    }
    this.userNameConditionError();
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
    // Map connection names to database type IDs
    const databaseTypeMap: { [key: string]: number } = {
      'POSTGRESQL': 1,
      'ORACLE': 3,
      'MICROSOFTSQLSERVER': 4,
      'SQLITE': 5,
      'MONGODB': 6,
      'CASSANDRA': 7,
      'SNOWFLAKE': 8,
      'MARIADB': 9,
      'IBMDB2': 10,
      'MICROSOFTACCESS': 11,
      'SYBASE': 12,
      'SAPHANA': 13,
      'SAPBW': 14,
      'MYSQL': 23
    };
    
    let database_type = databaseTypeMap[this.selectedConnection || 'POSTGRESQL'] || 1;
    
    // Build object based on connection type requirements
    let object: any = {
      database_type: database_type,
      connection_name: this.displayName,
    };

    // Add fields based on connection type
    const config = this.getConnectionConfig(this.selectedConnection || 'POSTGRESQL');
    
    if (config.fields.includes('hostname')) object.hostname = this.serverName;
    if (config.fields.includes('port')) object.port = this.portName;
    if (config.fields.includes('database')) object.database = this.databaseName;
    if (config.fields.includes('username')) object.username = this.userName;
    if (config.fields.includes('password')) object.password = this.password;
    if (config.fields.includes('schema')) object.schema = this.selectedSchema;
    if (config.fields.includes('serviceName')) object.service_name = this.serviceName;
    if (config.fields.includes('databasePath')) object.path = this.databasePath;
    if (config.fields.includes('authDatabase')) object.auth_database = this.authDatabase;
    if (config.fields.includes('keyspace')) object.keyspace = this.keyspace;
    if (config.fields.includes('account')) object.account = this.account;
    if (config.fields.includes('warehouse')) object.warehouse = this.warehouse;
    if (config.fields.includes('role')) object.role = this.role;
    
    // Set service_name to null if not required
    if (!config.requiresServiceName) {
      object.service_name = null;
    }
    
    console.log(object);

    this.workbenchService.databaseConnection(object).subscribe({
      next: (response) => {
        this.toasterservice.success(response.message,'success',{ positionClass: 'toast-top-right'});
        console.log('Connection successful:', response);
        this.resetForm();
        this.routeToViewConnection();
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
        this.resetForm();
        this.isEditPreview = false;
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
        
        // Map database_type ID to connection name
        const databaseTypeReverseMap: { [key: number]: string } = {
          1: 'POSTGRESQL',
          3: 'ORACLE',
          4: 'MICROSOFTSQLSERVER',
          5: 'SQLITE',
          6: 'MONGODB',
          7: 'CASSANDRA',
          8: 'SNOWFLAKE',
          9: 'MARIADB',
          10: 'IBMDB2',
          11: 'MICROSOFTACCESS',
          12: 'SYBASE',
          13: 'SAPHANA',
          14: 'SAPBW',
          23: 'MYSQL'
        };
        
        this.selectedConnection = databaseTypeReverseMap[response.database_type] || 'POSTGRESQL';
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

  onAuthFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.selectedAuthFile = input.files[0];
      console.log('Auth file selected:', this.selectedAuthFile.name);
    }
    input.value = '';
  }

  clearAuthFile() {
    this.selectedAuthFile = null;
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
        this.resetForm();
        if(this.isEditPreview){
          this.isEditPreview = false;
          this.getConnectionList();
        } else{
          this.routeToViewConnection();
        }
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
        // this.openUploadModal(modal);
        this.displayName = response.connection_name;
        this.selectedConnection = 'CSV';
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
    this.isLoading = true;
    this.workbenchService.disableLoaderForNextRequest();
    this.workbenchService.getConnectionsList(this.page, this.pageSize, this.searchConnections).subscribe({
      next: (response: any) => {
        this.connectionList = response.data;
        this.totalItems = response.total_items ?? 10;
        console.log('Connections fetched successfully:', this.connectionList);
        this.isLoading = false;
      },
      error: (err) => {
        this.isLoading = false;
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
    this.selectedConnection = null;
    this.errorCheck();
  }

  onPageSizeChange() {
      const totalPages = Math.ceil(this.totalItems / this.pageSize);
      if (this.page > totalPages) {
        this.page = 1;
      }
      this.getConnectionList();
  }

  routeToNewConnection(){
    this.router.navigate(['/datamplify/easyConnection/newConnection']);
  }
  
  routeToViewConnection(){
    this.router.navigate(['/datamplify/easyConnection']);
  }

  connectionListIcons: any = {
    // Relational Databases
    MYSQL: { type: 'emoji', value: '🐬' },
    POSTGRESQL: { type: 'emoji', value: '🐘' },
    MARIADB: { type: 'emoji', value: '🦭' },
    SQLITE: { type: 'emoji', value: '💾' },
    MICROSOFTSQLSERVER: { type: 'emoji', value: '🖥️' },
    SYBASE: { type: 'emoji', value: '📊' },
    IBMDB2: { type: 'emoji', value: '💼' },
    MICROSOFTACCESS: { type: 'emoji', value: '📁' },
    // NoSQL Databases
    MONGODB: { type: 'emoji', value: '🍃' },
    CASSANDRA: { type: 'emoji', value: '💿' },
    // Cloud Data Warehouse
    SNOWFLAKE: { type: 'emoji', value: '❄️' },
    // Enterprise Databases
    ORACLE: { type: 'emoji', value: '🏛️' },
    SAPHANA: { type: 'emoji', value: '🔷' },
    'SAP HANA': { type: 'emoji', value: '🔷' },
    SAPBW: { type: 'emoji', value: '🔶' },
    'SAP BW': { type: 'emoji', value: '🔶' },
    // File Sources
    CSV: { type: 'emoji', value: '📑' },
    EXCEL: { type: 'emoji', value: '📊' },
    JSON: { type: 'emoji', value: '📋' },
    XML: { type: 'emoji', value: '📄' },
    PARQUET: { type: 'emoji', value: '📦' },
    AVRO: { type: 'emoji', value: '🗃️' },
    ORC: { type: 'emoji', value: '📚' },
    TXT: { type: 'emoji', value: '📝' },
  };
  categories = [
    { name: 'Relational Database', icon: '🛢️', description: 'Traditional SQL databases',count:'10' },
    { name: 'NoSQL Database', icon: '📡', description: 'Document, Key-Value databases',count:'2' },
    { name: 'Cloud Data Warehouse', icon: '☁️', description: 'Cloud-based data warehouses',count:'1' },
    { name: 'Enterprise Database', icon: '🏢', description: 'Enterprise database systems',count:'2' },
    { name: 'File Source', icon: '📂', description: 'File-based data sources',count:'8' },
  ];
  connectionTypes: { [key: string]: { name: string; icon?: string; description: string; image?: string; svg?: string }[] } = {
    "Relational Database": [
      { name: "MYSQL", icon: "🐬", description: "Popular open-source relational database" },
      { name: "POSTGRESQL", icon: "🐘", description: "Advanced open-source relational database" },
      { name: "MARIADB", icon: "🦭", description: "MySQL-compatible database" },
      { name: "SQLITE", icon: "💾", description: "Lightweight embedded database" },
      { name: "MICROSOFTSQLSERVER", icon: "🖥️", description: "Microsoft SQL Server database" },
      { name: "SYBASE", icon: "📊", description: "Sybase database system" },
      { name: "IBMDB2", icon: "💼", description: "IBM DB2 database" },
      { name: "MICROSOFTACCESS", icon: "📁", description: "Microsoft Access database" },
    ],
    "NoSQL Database": [
      { name: "MONGODB", icon: "🍃", description: "Document-oriented NoSQL database" },
      { name: "CASSANDRA", icon: "💿", description: "Distributed NoSQL database" },
    ],
    "Cloud Data Warehouse": [
      { name: "SNOWFLAKE", icon: "❄️", description: "Cloud data warehouse platform" },
    ],
    "Enterprise Database": [
      { name: "ORACLE", icon: "🏛️", description: "Enterprise relational database" },
      { name: "SAPHANA", icon: "🔷", description: "SAP HANA in-memory database" },
      { name: "SAPBW", icon: "🔶", description: "SAP Business Warehouse" },
    ],
    "File Source": [
      { name: "CSV", icon: "📑", description: "Comma-separated values file" },
      { name: "EXCEL", icon: "📊", description: "Microsoft Excel spreadsheet" },
      { name: "JSON", icon: "📋", description: "JavaScript Object Notation file" },
      { name: "XML", icon: "📄", description: "Extensible Markup Language file" },
      { name: "PARQUET", icon: "📦", description: "Columnar storage file format" },
      { name: "AVRO", icon: "🗃️", description: "Data serialization format" },
      { name: "ORC", icon: "📚", description: "Optimized Row Columnar format" },
      { name: "TXT", icon: "📝", description: "Plain text file" },
    ],
  };

  getSafeSvg(svg: string): SafeHtml {
    return this.sanitizer.bypassSecurityTrustHtml(svg);
  }

  // Get connection configuration for each database type
  getConnectionConfig(connectionType: string): any {
    const configs: { [key: string]: any } = {
      'POSTGRESQL': {
        fields: ['hostname', 'port', 'database', 'username', 'password', 'schema'],
        defaultPort: '5432',
        requiresSchema: true,
        requiresServiceName: false,
        requiresPath: false
      },
      'MYSQL': {
        fields: ['hostname', 'port', 'database', 'username', 'password'],
        defaultPort: '3306',
        requiresSchema: false,
        requiresServiceName: false,
        requiresPath: false
      },
      'ORACLE': {
        fields: ['hostname', 'port', 'serviceName', 'username', 'password'],
        defaultPort: '1521',
        requiresSchema: false,
        requiresServiceName: true,
        requiresPath: false
      },
      'MICROSOFTSQLSERVER': {
        fields: ['hostname', 'port', 'database', 'username', 'password'],
        defaultPort: '1433',
        requiresSchema: false,
        requiresServiceName: false,
        requiresPath: false
      },
      'SQLITE': {
        fields: ['databasePath'],
        defaultPort: '',
        requiresSchema: false,
        requiresServiceName: false,
        requiresPath: true
      },
      'MONGODB': {
        fields: ['hostname', 'port', 'database', 'username', 'password', 'authDatabase'],
        defaultPort: '27017',
        requiresSchema: false,
        requiresServiceName: false,
        requiresPath: false
      },
      'CASSANDRA': {
        fields: ['hostname', 'port', 'keyspace', 'username', 'password'],
        defaultPort: '9042',
        requiresSchema: false,
        requiresServiceName: false,
        requiresPath: false
      },
      'SNOWFLAKE': {
        fields: ['account', 'warehouse', 'database', 'schema', 'username', 'password', 'role'],
        defaultPort: '443',
        requiresSchema: true,
        requiresServiceName: false,
        requiresPath: false
      },
      'MARIADB': {
        fields: ['hostname', 'port', 'database', 'username', 'password'],
        defaultPort: '3306',
        requiresSchema: false,
        requiresServiceName: false,
        requiresPath: false
      },
      'IBMDB2': {
        fields: ['hostname', 'port', 'database', 'username', 'password'],
        defaultPort: '50000',
        requiresSchema: false,
        requiresServiceName: false,
        requiresPath: false
      },
      'MICROSOFTACCESS': {
        fields: ['databasePath'],
        defaultPort: '',
        requiresSchema: false,
        requiresServiceName: false,
        requiresPath: true
      },
      'SYBASE': {
        fields: ['hostname', 'port', 'database', 'username', 'password'],
        defaultPort: '5000',
        requiresSchema: false,
        requiresServiceName: false,
        requiresPath: false
      },
      'SAPHANA': {
        fields: ['hostname', 'port', 'database', 'username', 'password'],
        defaultPort: '30015',
        requiresSchema: false,
        requiresServiceName: false,
        requiresPath: false
      },
      'SAPBW': {
        fields: ['hostname', 'port', 'database', 'username', 'password'],
        defaultPort: '30015',
        requiresSchema: false,
        requiresServiceName: false,
        requiresPath: false
      }
    };
    
    return configs[connectionType] || configs['POSTGRESQL'];
  }

  // Check if field is required for current connection
  isFieldRequired(fieldName: string): boolean {
    if (!this.selectedConnection) return false;
    const config = this.getConnectionConfig(this.selectedConnection);
    return config.fields.includes(fieldName);
  }

  // Set default port when connection type is selected
  setDefaultPort() {
    if (this.selectedConnection) {
      const config = this.getConnectionConfig(this.selectedConnection);
      if (config.defaultPort && !this.portName) {
        this.portName = config.defaultPort;
      }
    }
  }

  categorySelect(categoryName: string) {
    this.selectedCategory = categoryName;
    console.log(this.selectedCategory);
    this.viewNewConnection = false;
    this.showRelational = false;
    this.showNoSQL = false;
    this.showCloudWarehouse = false;
    this.showEnterprise = false;
    this.showFiles = false;
    switch (categoryName) {
      case 'Relational Database':
        this.showRelational = true;
        break;
      case 'NoSQL Database':
        this.showNoSQL = true;
        break;
      case 'Cloud Data Warehouse':
        this.showCloudWarehouse = true;
        break;
      case 'Enterprise Database':
        this.showEnterprise = true;
        break;
      case 'File Source':
        this.showFiles = true;
        break;
    }
  }
  goBackToCategories() {
    this.showRelational = false;
    this.showNoSQL = false;
    this.showCloudWarehouse = false;
    this.showEnterprise = false;
    this.showFiles = false;
    this.viewNewConnection = true;
    this.selectedCategory = null;
  }
  selectConnection(connName: string) {
    this.selectedConnection = connName;
    this.setDefaultPort(); // Set default port for the selected connection
    this.getSpecificConnections(this.selectedConnection);
  }
  getSpecificConnections(selectedConnection:any){
    this.isLoading = true;
    // Map connection names to database/file type IDs
    const connectionTypeMap: { [key: string]: number } = {
      'POSTGRESQL': 1,
      'ORACLE': 3,
      'MICROSOFTSQLSERVER': 4,
      'SQLITE': 5,
      'MONGODB': 6,
      'CASSANDRA': 7,
      'SNOWFLAKE': 8,
      'MARIADB': 9,
      'IBMDB2': 10,
      'MICROSOFTACCESS': 11,
      'SYBASE': 12,
      'SAPHANA': 13,
      'SAPBW': 14,
      'CSV': 15,
      'EXCEL': 16,
      'JSON': 17,
      'XML': 18,
      'PARQUET': 19,
      'AVRO': 20,
      'ORC': 21,
      'TXT': 22,
      'MYSQL': 23
    };
    
    let connectionTypeId = connectionTypeMap[selectedConnection] || 1;
    this.workbenchService.disableLoaderForNextRequest();
    this.workbenchService.getConnectionsForEtl(connectionTypeId).subscribe({
      next: (data) => {
        console.log(data);
        this.existingConnections = data.data;
        this.isLoading = false;
      },
      error: (error: any) => {
        console.log(error);
        this.toasterservice.error(error.error.message, 'error', { positionClass: 'toast-top-right' });
        this.isLoading = false;
      }
    });
  }
  getConnectionAsset(connName: string) {
    // Find the connection object from connectionTypes
    for (const category in this.connectionTypes) {
      const found = this.connectionTypes[category].find(c => c.name === connName);
      if (found) {
        if (found.icon) return { type: 'icon', value: found.icon };
        if (found.image) return { type: 'image', value: found.image };
        if (found.svg) return { type: 'svg', value: this.sanitizer.bypassSecurityTrustHtml(found.svg) };
      }
    }
    // fallback
    return { type: 'icon', value: '🔗' };
  }

  goBackToSubCategories() {
    this.showRelational = false;
    this.showNoSQL = false;
    this.showCloudWarehouse = false;
    this.showEnterprise = false;
    this.showFiles = false;
    this.viewNewConnection = false;
    this.selectedConnection = null;
    this.existingConnections = [];

    switch (this.selectedCategory) {
      case 'Relational Database':
        this.showRelational = true;
        break;
      case 'NoSQL Database':
        this.showNoSQL = true;
        break;
      case 'Cloud Data Warehouse':
        this.showCloudWarehouse = true;
        break;
      case 'Enterprise Database':
        this.showEnterprise = true;
        break;
      case 'File Source':
        this.showFiles = true;
        break;
    }
  }
}
