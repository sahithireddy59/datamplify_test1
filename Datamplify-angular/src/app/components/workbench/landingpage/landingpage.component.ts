import { ChangeDetectorRef, Component, OnInit, ViewChild } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { NgbModal, NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { WorkbenchService } from '../workbench.service';
import Swal from 'sweetalert2';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { InsightsButtonComponent } from '../insights-button/insights-button.component';
import { ViewTemplateDrivenService } from '../view-template-driven.service';
import { NgSelectModule } from '@ng-select/ng-select';
import { ToastrService } from 'ngx-toastr';
import { LoaderService } from '../../../shared/services/loader.service';

@Component({
  selector: 'app-landingpage',
  standalone: true,
  imports: [NgbModule,CommonModule,FormsModule,InsightsButtonComponent,NgSelectModule],
  templateUrl: './landingpage.component.html',
  styleUrl: './landingpage.component.scss'
})

export class LandingpageComponent implements OnInit {
wholeSearch:string = '';
roleDetails = [] as any;
selectedRoleIds = [] as any;
selectedRoleIdsToNumbers = [] as any;
usersOnSelectedRole =[] as any;
selectedUserIds = [] as any;
selectedUserIdsToNumbers = [] as any;
port:any;
host:any;

dataFlowList: any[] = [];
jobFlowList: any[] = [];
monitorsList: any[] = [];
connectionList:any[]=[];
showAllDataFlows: boolean = true;
showAllJobFlows: boolean = true;
showAllMonitors: boolean = true;

constructor(private router:Router,private workbenchService:WorkbenchService,private templateService:ViewTemplateDrivenService,public modalService:NgbModal,private cdr: ChangeDetectorRef,private toasterservice:ToastrService,private loaderService : LoaderService, private toasterService: ToastrService) {
}

ngOnInit(){
  this.loaderService.hide();
  this.getFlowboardList();
  this.getTaskplanList();
  this.getMonitorList();
  this.getConnectionList();
  this.getHostAndPort();
}
  getFlowboardList() {
    this.workbenchService.getFlowboardList(1, 12, this.wholeSearch, 'dataflow').subscribe({
      next: (data: any) => {
        this.dataFlowList = data.data || [];
      },
      error: (error: any) => {
        this.toasterservice.error(error.error.message, 'error', { positionClass: 'toast-top-right' });
      }
    });
  }

  getTaskplanList() {
    this.workbenchService.getTaskPlanList(1, 12, this.wholeSearch, 'jobflow').subscribe({
      next: (data: any) => {
        this.jobFlowList = data.data || [];
      },
      error: (error: any) => {
        this.toasterservice.error(error.error.message, 'error', { positionClass: 'toast-top-right' });
      }
    });
  }

  getMonitorList() {
    this.workbenchService.getDags(12, 1, this.wholeSearch).subscribe({
      next: (data: any) => {
        this.monitorsList = data?.dags || [];
      },
      error: (error: any) => {
        this.toasterservice.error(error.error.message, 'error', { positionClass: 'toast-top-right' });
      }
    });
  }

  getConnectionList(): void {
    this.workbenchService.getConnectionsList(1, 12, this.wholeSearch).subscribe({
      next: (response: any) => {
        this.connectionList = response.data || [];
        console.log('Connections fetched successfully:', this.connectionList);
      },
      error: (err) => {
        this.toasterservice.error(err.error.message,'error',{ positionClass: 'toast-top-right'});
        console.error('Error fetching connections:', err);
      }
    });
  }

  goToDataFlowList() {
    this.router.navigate(['/datamplify/flowboardList']);
  }
  goToJobFlowList() {
    this.router.navigate(['/datamplify/taskplanList']);
  }
  goToMonitorList() {
    this.router.navigate(['/datamplify/monitorList']);
  }
  goToConnectionList() {
    this.router.navigate(['/datamplify/easyConnection']);
  }

  goToDataFlow() {
    this.router.navigate(['/datamplify/flowboardList/flowboard']);
  }
  goToJobFlow() {
    this.router.navigate(['/datamplify/taskplanList/taskplan']);
  }
  goToNewConnection(){
    this.router.navigate(['/datamplify/home/easyConnection']);
  }

  editDataFlow(id: any) {
    const encodedId = btoa(id.toString());
    this.router.navigate(['/datamplify/flowboardList/flowboard/' + encodedId]);
  }
  editJobFlow(id: any) {
    const encodedId = btoa(id.toString());
    this.router.navigate(['/datamplify/taskplanList/taskplan/' + encodedId]);
  }
  goToMonitor(id: any) {
    const encodedId = btoa(id.toString());
    this.router.navigate(['/datamplify/monitorList/monitor/' + encodedId]);
  }
  deleteFlow(flow: any, type: string) {
    Swal.fire({
      position: "center",
      icon: "question",
      title: `Delete ${flow.Flow_name} ${type === 'dataflow' ? 'flowboard' : 'taskplan'} ?`,
      text: "This action cannot be undone. Are you sure you want to proceed?",
      showConfirmButton: true,
      showCancelButton: true,
      confirmButtonText: 'Yes',
      cancelButtonText: 'No',
    }).then((result) => {
      if (result.isConfirmed) {
        if (type === 'dataflow') {
          this.workbenchService.deleteFlowboard(flow.id).subscribe({
            next: (response) => {
              console.log(response);
              this.getFlowboardList();
              this.toasterService.success(response.message, 'success', { positionClass: 'toast-top-right' });
            },
            error: (error) => {
              console.log(error);
              this.toasterService.error(error.error.message, 'error', { positionClass: 'toast-top-right' });
            }
          })
        } else {
          this.workbenchService.deleteTaskPlan(flow.id).subscribe({
            next: (response) => {
              console.log(response);
              this.getTaskplanList();
              this.toasterService.success(response.message, 'success', { positionClass: 'toast-top-right' });
            },
            error: (error) => {
              console.log(error);
              this.toasterService.error(error.error.message, 'error', { positionClass: 'toast-top-right' });
            }
          })
        }
      }
    })
  }

  getHostAndPort(): void {
    const { hostname, port } = window.location;
    this.host = hostname;
    this.port = port;
    console.log('port', this.port, 'host', this.host)
  }
  totalSearch() {
    this.getFlowboardList();
    this.getTaskplanList();
    // this.getMonitorList();
    this.getConnectionList();
  }

  getRoleDetailsDshboard() {
    this.workbenchService.getRoleDetailsDshboard().subscribe({
      next: (data) => {
        console.log('dashboardroledetails', data);
        this.roleDetails = data;
        // this.getUsersforRole();
      },
      error: (error) => {
        console.log(error);
        Swal.fire({
          icon: 'error',
          title: 'oops!',
          text: error.error.message,
          width: '400px',
        })
      }
    })
  }
  getUsersforRole() {
    const obj = {
      role_ids: this.selectedRoleIdsToNumbers
    }
    this.workbenchService.getUsersOnRole(obj).subscribe({
      next: (data) => {
        this.usersOnSelectedRole = data
        console.log('usersOnselecetdRoles', data);
      },
      error: (error) => {
        console.log(error);
        Swal.fire({
          icon: 'error',
          title: 'oops!',
          text: error.error.message,
          width: '400px',
        })
      }
    })
  }

  fallbackCopyTextToClipboard(text: string): void {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';  // Avoid scrolling to bottom
    textArea.style.opacity = '0';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    try {
      const successful = document.execCommand('copy');
      if (successful) {
        this.toasterservice.success('Link Copied', 'success', { positionClass: 'toast-center-center' });
      } else {
        console.error('Fallback: Could not copy text');
      }
    } catch (err) {
      console.error('Fallback: Unable to copy', err);
    }
    document.body.removeChild(textArea);
  }
  onRolesChange(selected: number[]) {
    this.selectedRoleIds = selected
    this.selectedRoleIdsToNumbers = selected.map(value => Number(value));
    console.log(this.selectedRoleIds);
    if (this.selectedRoleIds.length === 0) {
      this.selectedUserIds = [];
      this.selectedUserIdsToNumbers = [];
      return;
    }
    const obj = { role_ids: this.selectedRoleIdsToNumbers };

    this.workbenchService.getUsersOnRole(obj).subscribe({
      next: (data) => {
        console.log('Updated users for selected roles:', data);
        this.usersOnSelectedRole = data;
        const validUserIds = new Set(data.map((user: { user_id: any; }) => String(user.user_id)));

        const prevSelectedUsers = [...this.selectedUserIds]; // Backup for debugging
        this.selectedUserIds = this.selectedUserIds.filter((userId: any) =>
          validUserIds.has(String(userId)) // Convert to string for safe comparison
        );

        this.selectedUserIdsToNumbers = this.selectedUserIds.map((value: any) => Number(value));

        // Debugging logs
        console.log('Previous selected users:', prevSelectedUsers);
        console.log('Valid user IDs after role change:', [...validUserIds]);
        console.log('Filtered selected users:', this.selectedUserIds);
      },
      error: (error) => {
        console.log(error);
        Swal.fire({
          icon: 'error',
          title: 'Oops!',
          text: error.error.message,
          width: '400px',
        });
      }
    });
  }
  getSelectedUsers(selected: number[]) {
    this.selectedUserIds = selected;
    this.selectedUserIdsToNumbers = this.selectedUserIds.map((value: any) => Number(value));
    console.log(this.selectedUserIds)

    // this.selectedUserIds = selected
  }

  dashboard(){
    this.router.navigate(['/datamplify/home/dashboard']);
  }
}
