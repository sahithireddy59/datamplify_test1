import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators, FormsModule } from '@angular/forms';
import { NgbActiveModal, NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { SchedulerDto, SchedulerMode, SchedulerService } from '../../../services/scheduler.service';
import cronstrue from 'cronstrue';
import { parseExpression } from 'cron-parser';

@Component({
  selector: 'app-scheduler-modal',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FormsModule, NgbModule],
  templateUrl: './scheduler-modal.component.html',
  styleUrls: ['./scheduler-modal.component.scss']
})
export class SchedulerModalComponent {
  @Input() existing?: SchedulerDto | null = null;
  @Input() defaultDagId?: string | null = null;
  @Input() suggestedName?: string | null = null;
  @Input() flowboardId?: string | null = null; // UUID of FlowBoard

  saving = false;
  cronHuman = '';
  nextRuns: string[] = [];

  form = this.fb.group({
    id: [null as number | null],
    name: ['', [Validators.required, Validators.maxLength(120)]],
    mode: ['trigger' as SchedulerMode, [Validators.required]],
    schedule: ['0 0 * * *'],
    start_date: [null as string | null],
    timezone: ['Asia/Kolkata', [Validators.required]],
    catchup: [false],
    max_active_runs: [1, [Validators.min(1)]],
    enabled: [true],
    target_dag_id: [null as string | null],
    bash_command: [null as string | null],
  });

  constructor(
    private fb: FormBuilder,
    public activeModal: NgbActiveModal,
    private svc: SchedulerService,
    private toast: ToastrService,
  ) {}

  ngOnInit() {
    if (this.existing) {
      this.form.patchValue(this.existing as any);
    } else {
      if (this.defaultDagId) this.form.patchValue({ target_dag_id: this.defaultDagId });
      if (this.suggestedName) this.form.patchValue({ name: this.suggestedName });
      // Try to load an existing scheduler for this flowboard
      if (this.flowboardId) {
        this.svc.listByFlowboard(this.flowboardId).subscribe({
          next: (items: SchedulerDto[]) => {
            if (items && items.length) {
              this.existing = items[0];
              this.form.patchValue(this.existing as any);
            }
            this.updateCronPreview();
          },
          error: () => {
            this.updateCronPreview();
          }
        });
        return; // updateCronPreview will be called in subscribe
      }
    }
    this.updateCronPreview();
    this.form.get('schedule')?.valueChanges.subscribe(() => this.updateCronPreview());
  }

  private updateCronPreview() {
    const cron = this.form.get('schedule')?.value || '';
    try {
      this.cronHuman = cron ? cronstrue.toString(cron) : 'No schedule (manual)';
    } catch {
      this.cronHuman = cron ? `Cron: ${cron}` : 'No schedule (manual)';
    }

    this.nextRuns = [];
    if (!cron) return;
    try {
      const tz = this.form.value.timezone || 'UTC';
      const expr = parseExpression(cron, { tz });
      for (let i = 0; i < 5; i++) {
        const d = expr.next().toDate();
        this.nextRuns.push(d.toLocaleString());
      }
    } catch {
      // invalid cron, ignore
    }
  }

  onModeChange() {
    const mode = this.form.value.mode;
    if (mode === 'bash') {
      this.form.get('bash_command')?.addValidators([Validators.required]);
      this.form.get('target_dag_id')?.clearValidators();
    } else {
      this.form.get('target_dag_id')?.addValidators([Validators.required]);
      this.form.get('bash_command')?.clearValidators();
    }
    this.form.get('bash_command')?.updateValueAndValidity();
    this.form.get('target_dag_id')?.updateValueAndValidity();
  }

  save() {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.saving = true;
    const raw: any = { ...(this.form.value as any) };
    // Trim name
    if (typeof raw.name === 'string') raw.name = raw.name.trim();
    // Do not send start_date if empty/null; backend has default and may not accept null
    if (!raw.start_date) delete raw.start_date;
    // If schedule is empty string, send null
    if (raw.schedule === '') raw.schedule = null;
    // Mode-specific optional fields: drop the irrelevant one if empty
    if (raw.mode === 'bash') {
      if (!raw.bash_command) delete raw.bash_command;
      delete raw.target_dag_id; // not needed for bash
    } else {
      if (!raw.target_dag_id) delete raw.target_dag_id;
      delete raw.bash_command; // not needed for trigger
    }
    // Attach flowboard
    raw.flowboard = this.flowboardId || null;
    const payload: SchedulerDto = raw;

    const obs = payload.id ? this.svc.update(payload.id!, payload) : this.svc.create(payload);

    obs.subscribe({
      next: (res) => {
        this.toast.success('Scheduler saved');
        this.activeModal.close(res);
      },
      error: (err) => {
        this.saving = false;
        const msg = err?.error?.message || 'Failed to save scheduler';
        this.toast.error(msg);
      }
    });
  }

  onPresetChange(value: string) {
    if (!value) return;
    this.form.patchValue({ schedule: value });
    this.updateCronPreview();
  }
}
