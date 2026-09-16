declare module '*.vue' {
    import type { DefineComponent } from 'vue';
    const component: DefineComponent;
    export default component;
}

declare module '@fullcalendar/vue3';
declare module '@fullcalendar/daygrid';
declare module '@fullcalendar/timegrid';
declare module '@fullcalendar/interaction';
