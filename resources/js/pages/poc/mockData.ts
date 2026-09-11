export interface Appointment {
    id: string;
    title: string;
    start: string; // ISO string e.g. "2026-09-11T09:00:00"
    end: string;
    branchId: 'b1' | 'b2' | 'b3';
    patientName: string;
    patientPhone: string;
    doctorName: string;
    treatment: string;
    price: number;
    status: 'pending_bill' | 'confirmed' | 'paid';
    notes?: string;
}

export interface Branch {
    id: 'b1' | 'b2' | 'b3';
    name: string;
    address: string;
    color: string;
    badgeClass: string;
}

export interface Doctor {
    id: string;
    name: string;
    specialty: string;
}

export const clinicBranches: Branch[] = [
    {
        id: 'b1',
        name: 'สาขา สยามสแควร์ (Siam Square)',
        address: 'อาคารสยามสแควร์วัน ชั้น 4',
        color: '#3b82f6',
        badgeClass: 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300 border-blue-200 dark:border-blue-800'
    },
    {
        id: 'b2',
        name: 'สาขา อารีย์ (Ari)',
        address: 'พหลโยธินซอย 7 อาคารลาวิลล่า',
        color: '#10b981',
        badgeClass: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800'
    },
    {
        id: 'b3',
        name: 'สาขา ทองหล่อ (Thong Lo)',
        address: 'สุขุมวิท 55 ทองหล่อซอย 10',
        color: '#8b5cf6',
        badgeClass: 'bg-purple-100 text-purple-800 dark:bg-purple-950 dark:text-purple-300 border-purple-200 dark:border-purple-800'
    }
];

export const clinicDoctors: Doctor[] = [
    { id: 'd1', name: 'ทพ. ภัทร วาจาสัตย์', specialty: 'ทันตกรรมทั่วไป & ขูดหินปูน' },
    { id: 'd2', name: 'ทพญ. นภัสสร ศิริมงคล', specialty: 'จัดฟัน & ทันตกรรมเพื่อความงาม' },
    { id: 'd3', name: 'ทพ. ธนกฤต มั่นคง', specialty: 'ศัลยกรรมช่องปาก & รากฟันเทียม' }
];

export const treatmentOptions = [
    { name: 'ขูดหินปูน & ขัดฟัน (Scaling)', price: 900 },
    { name: 'อุดฟันคอมโพสิต (Composite Filling)', price: 1500 },
    { name: 'ฟอกสีฟัน Cool Light (Whitening)', price: 4900 },
    { name: 'จัดฟันใส Invisalign (Consultation)', price: 3500 },
    { name: 'ผ่าฟันคุด (Wisdom Tooth Surgery)', price: 2800 },
    { name: 'รักษารากฟัน (Root Canal Treatment)', price: 6500 }
];

/**
 * Generate initial realistic appointments around the current date
 */
export function getInitialAppointments(): Appointment[] {
    const now = new Date();
    const y = now.getFullYear();
    const m = String(now.getMonth() + 1).padStart(2, '0');
    const d = String(now.getDate()).padStart(2, '0');
    const dateStr = `${y}-${m}-${d}`;

    // Tomorrow
    const tom = new Date(now);
    tom.setDate(tom.getDate() + 1);
    const tomStr = `${tom.getFullYear()}-${String(tom.getMonth() + 1).padStart(2, '0')}-${String(tom.getDate()).padStart(2, '0')}`;

    return [
        // Branch 1 - สยามสแควร์
        {
            id: 'apt-101',
            title: 'ขูดหินปูน & ขัดฟัน',
            start: `${dateStr}T09:00:00`,
            end: `${dateStr}T10:00:00`,
            branchId: 'b1',
            patientName: 'นาย สมชาย ใจดี',
            patientPhone: '081-234-5678',
            doctorName: 'ทพ. ภัทร วาจาสัตย์',
            treatment: 'ขูดหินปูน & ขัดฟัน (Scaling)',
            price: 900,
            status: 'pending_bill',
            notes: 'คนไข้มีเสียวฟันบริเวณกรามล่างซ้าย'
        },
        {
            id: 'apt-102',
            title: 'จัดฟันใส Invisalign Follow-up',
            start: `${dateStr}T11:00:00`,
            end: `${dateStr}T12:30:00`,
            branchId: 'b1',
            patientName: 'นางสาว แพรวา วงศ์สว่าง',
            patientPhone: '089-876-5432',
            doctorName: 'ทพญ. นภัสสร ศิริมงคล',
            treatment: 'จัดฟันใส Invisalign (Consultation)',
            price: 3500,
            status: 'confirmed',
            notes: 'ตรวจรับถาดชุดที่ 8'
        },
        {
            id: 'apt-103',
            title: 'ฟอกสีฟัน Cool Light',
            start: `${dateStr}T14:00:00`,
            end: `${dateStr}T15:30:00`,
            branchId: 'b1',
            patientName: 'นาย กิตติศักดิ์ พรหมดี',
            patientPhone: '085-111-2233',
            doctorName: 'ทพญ. นภัสสร ศิริมงคล',
            treatment: 'ฟอกสีฟัน Cool Light (Whitening)',
            price: 4900,
            status: 'pending_bill'
        },

        // Branch 2 - อารีย์ (วันเดียวกัน เคสแตกต่างกันเพื่อทดสอบ Filter)
        {
            id: 'apt-201',
            title: 'ผ่าฟันคุด กรามล่างขวา',
            start: `${dateStr}T09:30:00`,
            end: `${dateStr}T11:00:00`,
            branchId: 'b2',
            patientName: 'นางสาว ณิชา เจริญสุข',
            patientPhone: '082-456-7890',
            doctorName: 'ทพ. ธนกฤต มั่นคง',
            treatment: 'ผ่าฟันคุด (Wisdom Tooth Surgery)',
            price: 2800,
            status: 'pending_bill',
            notes: 'คนไข้แพ้ยา Penicillin'
        },
        {
            id: 'apt-202',
            title: 'อุดฟันคอมโพสิต 2 ซี่',
            start: `${dateStr}T13:00:00`,
            end: `${dateStr}T14:15:00`,
            branchId: 'b2',
            patientName: 'นาย ธนพล รัตนโกสินทร์',
            patientPhone: '086-777-8899',
            doctorName: 'ทพ. ภัทร วาจาสัตย์',
            treatment: 'อุดฟันคอมโพสิต (Composite Filling)',
            price: 3000,
            status: 'confirmed'
        },

        // Branch 3 - ทองหล่อ (วันเดียวกัน เคสแตกต่างกัน)
        {
            id: 'apt-301',
            title: 'รักษารากฟัน ครั้งที่ 1',
            start: `${dateStr}T10:00:00`,
            end: `${dateStr}T11:30:00`,
            branchId: 'b3',
            patientName: 'คุณ วิภาดา ศรีสวัสดิ์',
            patientPhone: '083-999-0011',
            doctorName: 'ทพ. ธนกฤต มั่นคง',
            treatment: 'รักษารากฟัน (Root Canal Treatment)',
            price: 6500,
            status: 'pending_bill'
        },
        {
            id: 'apt-302',
            title: 'ขูดหินปูน & ขัดฟัน',
            start: `${dateStr}T15:00:00`,
            end: `${dateStr}T16:00:00`,
            branchId: 'b3',
            patientName: 'นาย สิทธิชัย วัฒนานนท์',
            patientPhone: '084-222-3344',
            doctorName: 'ทพ. ภัทร วาจาสัตย์',
            treatment: 'ขูดหินปูน & ขัดฟัน (Scaling)',
            price: 900,
            status: 'paid'
        },

        // Tomorrow Cases
        {
            id: 'apt-104',
            title: 'จัดฟันใส เช็กความคืบหน้า',
            start: `${tomStr}T10:30:00`,
            end: `${tomStr}T11:30:00`,
            branchId: 'b1',
            patientName: 'นาย พงศกร มหัทธนะ',
            patientPhone: '081-999-8888',
            doctorName: 'ทพญ. นภัสสร ศิริมงคล',
            treatment: 'จัดฟันใส Invisalign (Consultation)',
            price: 3500,
            status: 'confirmed'
        }
    ];
}
