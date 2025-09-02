import { Component } from '@angular/core';
import { SharedModule } from '../../../shared/sharedmodule';
import { CommonModule, DatePipe  } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { NgxPaginationModule } from 'ngx-pagination';
import { ToastrService } from 'ngx-toastr';
import { WorkbenchService } from '../workbench.service';
import { LoaderService } from '../../../shared/services/loader.service';
import { ActivatedRoute, Router } from '@angular/router';
import Swal from 'sweetalert2';
import { SchedulerModalComponent } from '../../scheduler/scheduler-modal/scheduler-modal.component';

@Component({
  selector: 'app-flowboard-list',
  standalone: true,
  imports: [SharedModule,CommonModule,FormsModule,NgbModule,NgxPaginationModule,DatePipe],
  templateUrl: './flowboard-list.component.html',
  styleUrl: './flowboard-list.component.scss'
})
export class FlowboardListComponent {
  gridView = false;
  page: any = 1;
  pageSize: any = 10;
  totalItems: any;
  search: string = '';
  dataFlowList: any[] = [];

  constructor(private toasterService: ToastrService, private workbechService: WorkbenchService, private loaderService: LoaderService, private router: Router, private route: ActivatedRoute, private modal: NgbModal) {
  }

  ngOnInit() {
    this.loaderService.hide();
    this.getFlowboardList();
  }

  getFlowboardList() {
    this.workbechService.getFlowboardList(this.page, this.pageSize, this.search, 'dataflow').subscribe({
      next: (data: any) => {
        console.log(data);
        this.dataFlowList = data.data;
        this.totalItems = data?.total_records;
        this.pageSize = data?.page_size;
        this.page = data?.page_number;
        if (this.dataFlowList.length === 0) {
          this.pageSize = 10;
          this.page = 1;
          this.totalItems = 0;
        }
      },
      error: (error: any) => {
        this.toasterService.error(error.error.message, 'error', { positionClass: 'toast-top-right' });
        console.log(error);
      }
    });
  }

  deleteFlowboard(flow: any) {
    Swal.fire({
      position: "center",
      icon: "question",
      title: `Delete ${flow.Flow_name} Flowboard ?`,
      text: "This action cannot be undone. Are you sure you want to proceed?",
      showConfirmButton: true,
      showCancelButton: true,
      confirmButtonText: 'Yes',
      cancelButtonText: 'No',
    }).then((result) => {
      if (result.isConfirmed) {
        this.workbechService.deleteFlowboard(flow.id).subscribe({
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
      }
    })
  }

  goToFlowboard() {
    this.router.navigate(['/datamplify/flowboardList/flowboard']);
  }

  editFlowboard(id: any) {
    const encodedId = btoa(id.toString());
    this.router.navigate(['/datamplify/flowboardList/flowboard/' + encodedId]);
  }

  onPageSizeChange() {
    // Reset to page 1 if you're on the last page and items may not fit
    const totalPages = Math.ceil(this.totalItems / this.pageSize);
    if (this.page > totalPages) {
      this.page = 1;
    }
    this.getFlowboardList();
  }

  openScheduler(flow: any) {
    const ref = this.modal.open(SchedulerModalComponent, { size: 'lg' });
    ref.componentInstance.defaultDagId = flow?.Flow_id;
    ref.componentInstance.suggestedName = `${flow?.Flow_name || 'Flow'}-scheduler`;
    ref.componentInstance.flowboardId = flow?.id;
    ref.result.then(() => {
      // no-op; could refresh a schedulers list if present
    }).catch(() => {});
  }
}
