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
  
  newFlowboard = {
    name: '',
    description: '',
    sourceTable: '',
    targetTable: '',
    aiProvider: 'heuristic'
  };

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

  openNewFlowboardModal(content: any) {
    // Reset form
    this.newFlowboard = {
      name: '',
      description: '',
      sourceTable: '',
      targetTable: '',
      aiProvider: 'heuristic'
    };
    this.modal.open(content, { size: 'lg' });
  }

  generateMappingDirectly(modal: any) {
    if (!this.newFlowboard.sourceTable || !this.newFlowboard.targetTable) {
      this.toasterService.warning('Please enter both source and target table names', 'Warning', { positionClass: 'toast-top-right' });
      return;
    }

    if (this.newFlowboard.aiProvider === 'heuristic') {
      this.toasterService.warning('Please select an AI provider (Google AI, Perplexity, or Ollama)', 'Warning', { positionClass: 'toast-top-right' });
      return;
    }

    // Show loading message
    this.toasterService.info('Generating mappings with AI...', 'Please wait', { positionClass: 'toast-top-right', timeOut: 3000 });

    // Create instruction from table names
    const instruction = `Analyze and map all columns from source table '${this.newFlowboard.sourceTable}' to target table '${this.newFlowboard.targetTable}'. Create intelligent mappings based on column names and data types.`;

    // For now, just show the instruction that will be used
    console.log('AI Instruction:', instruction);
    console.log('AI Provider:', this.newFlowboard.aiProvider);
    console.log('Source Table:', this.newFlowboard.sourceTable);
    console.log('Target Table:', this.newFlowboard.targetTable);

    // Store the data and navigate to FlowBoard with auto-generation enabled
    sessionStorage.setItem('flowboard_name', this.newFlowboard.name || 'AI_Generated_Flow');
    sessionStorage.setItem('flowboard_source_table', this.newFlowboard.sourceTable);
    sessionStorage.setItem('flowboard_target_table', this.newFlowboard.targetTable);
    sessionStorage.setItem('flowboard_ai_provider', this.newFlowboard.aiProvider);
    sessionStorage.setItem('flowboard_ai_instruction', instruction);
    sessionStorage.setItem('auto_generate_mapping', 'true');

    modal.close();
    this.toasterService.success('AI will generate mappings when you add nodes', 'Success', { positionClass: 'toast-top-right' });
    this.router.navigate(['/datamplify/flowboardList/flowboard']);
  }

  createFlowboard(modal: any) {
    if (!this.newFlowboard.name.trim()) {
      this.toasterService.warning('Please enter a FlowBoard name', 'Warning', { positionClass: 'toast-top-right' });
      return;
    }

    // Store FlowBoard metadata and AI table names
    sessionStorage.setItem('flowboard_name', this.newFlowboard.name);
    if (this.newFlowboard.description) {
      sessionStorage.setItem('flowboard_description', this.newFlowboard.description);
    }
    if (this.newFlowboard.sourceTable || this.newFlowboard.targetTable) {
      sessionStorage.setItem('flowboard_source_table', this.newFlowboard.sourceTable);
      sessionStorage.setItem('flowboard_target_table', this.newFlowboard.targetTable);
      sessionStorage.setItem('flowboard_ai_provider', this.newFlowboard.aiProvider);
    }

    modal.close();
    this.router.navigate(['/datamplify/flowboardList/flowboard']);
  }
}
