import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { NgbActiveModal, NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { FlowboardService, FlowboardListItem, FlowboardListResponse } from '../../../services/flowboard.service';

@Component({
  selector: 'app-flowboard-picker',
  standalone: true,
  imports: [CommonModule, FormsModule, NgbModule],
  templateUrl: './flowboard-picker.component.html',
  styleUrls: ['./flowboard-picker.component.scss']
})
export class FlowboardPickerComponent {
  loading = false;
  items: FlowboardListItem[] = [];
  search = '';
  page = 1;
  pageSize = 10;
  totalPages = 1;

  constructor(
    public activeModal: NgbActiveModal,
    private svc: FlowboardService,
    private toast: ToastrService,
  ) {}

  ngOnInit() {
    this.load();
  }

  load() {
    this.loading = true;
    this.svc.list({ search: this.search, page: this.page, page_size: this.pageSize }).subscribe({
      next: (res: FlowboardListResponse) => {
        this.items = res?.data || [];
        this.totalPages = res?.total_pages || 1;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.toast.error('Failed to load FlowBoards');
      }
    });
  }

  applySearch() {
    this.page = 1;
    this.load();
  }

  pick(it: FlowboardListItem) {
    this.activeModal.close(it);
  }

  nextPage() {
    if (this.page < this.totalPages) { this.page++; this.load(); }
  }

  prevPage() {
    if (this.page > 1) { this.page--; this.load(); }
  }
}
