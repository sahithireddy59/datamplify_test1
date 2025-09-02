import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NgbModal, NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { SchedulerDto, SchedulerService } from '../../../services/scheduler.service';
import { SchedulerModalComponent } from '../../scheduler/scheduler-modal/scheduler-modal.component';
import { FlowboardPickerComponent } from '../../scheduler/flowboard-picker/flowboard-picker.component';

@Component({
  selector: 'app-scheduler-list',
  standalone: true,
  imports: [CommonModule, NgbModule],
  templateUrl: './scheduler-list.component.html',
  styleUrls: ['./scheduler-list.component.scss']
})
export class SchedulerListComponent {
  loading = false;
  items: SchedulerDto[] = [];

  constructor(
    private svc: SchedulerService,
    private modal: NgbModal,
    private toast: ToastrService,
  ) {}

  ngOnInit() {
    this.load();
  }

  load() {
    this.loading = true;
    this.svc.list().subscribe({
      next: (res: SchedulerDto[]) => {
        this.items = res || [];
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.toast.error('Failed to load schedules');
      }
    })
  }

  create() {
    // Step 1: pick a FlowBoard
    const pickRef = this.modal.open(FlowboardPickerComponent, { size: 'lg', backdrop: 'static' });
    pickRef.result.then((flow: any) => {
      if (!flow?.id) return;
      // Step 2: open scheduler modal with selected flowboard
      const ref = this.modal.open(SchedulerModalComponent, { size: 'lg', backdrop: 'static' });
      const cmp = ref.componentInstance as SchedulerModalComponent;
      cmp.flowboardId = flow.id;
      cmp.suggestedName = `Schedule - ${flow.Flow_name}`;
      ref.result.then(() => this.load()).catch(() => {});
    }).catch(() => {});
  }

  edit(item: SchedulerDto) {
    const ref = this.modal.open(SchedulerModalComponent, { size: 'lg', backdrop: 'static' });
    (ref.componentInstance as SchedulerModalComponent).existing = item;
    ref.result.then(() => this.load()).catch(() => {});
  }

  remove(item: SchedulerDto) {
    if (!item.id) return;
    if (!confirm(`Delete scheduler "${item.name}"?`)) return;
    this.svc.delete(item.id).subscribe({
      next: () => {
        this.toast.success('Deleted');
        this.load();
      },
      error: () => this.toast.error('Delete failed')
    });
  }
}
