import { Component } from '@angular/core';
import { SharedModule } from '../../../shared/sharedmodule';
import { CommonModule, DatePipe  } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { NgxPaginationModule } from 'ngx-pagination';
import { ToastrService } from 'ngx-toastr';
import { WorkbenchService } from '../workbench.service';
import { LoaderService } from '../../../shared/services/loader.service';
import { ActivatedRoute, Router } from '@angular/router';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-monitor-list',
  standalone: true,
  imports: [SharedModule,CommonModule,FormsModule,NgbModule,NgxPaginationModule,DatePipe],
  templateUrl: './monitor-list.component.html',
  styleUrl: './monitor-list.component.scss'
})
export class MonitorListComponent {
  gridView = false;
  page: any = 1;
  pageSize: any = 10;
  totalItems: any;
  search: string = '';
  monitorsList: any[] = [];

  constructor(private toasterService: ToastrService, private workbechService: WorkbenchService, private loaderService: LoaderService, private router: Router, private route: ActivatedRoute) {
  }

  ngOnInit() {
    this.loaderService.hide();
    this.getMonitorList();
  }

  getMonitorList() {
    this.workbechService.getDags(this.pageSize, this.page, this.search).subscribe({
      next: (data: any) => {
        console.log(data);
        this.monitorsList = data?.dags;
        this.totalItems = data?.total_entries;
      },
      error: (error: any) => {
        this.toasterService.error(error.error.message, 'error', { positionClass: 'toast-top-right' });
        console.log(error);
      }
    });
  }

  goToMonitor(id: any) {
    const encodedId = btoa(id.toString());
    this.router.navigate(['/datamplify/monitorList/monitor/' + encodedId]);
  }

  onPageSizeChange() {
    // Reset to page 1 if you're on the last page and items may not fit
    const totalPages = Math.ceil(this.totalItems / this.pageSize);
    if (this.page > totalPages) {
      this.page = 1;
    }
    this.getMonitorList();
  }
}
