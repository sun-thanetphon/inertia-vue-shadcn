<?php

use App\Http\Controllers\UserController;
use Illuminate\Support\Facades\Route;

Route::inertia('/', 'Welcome')->name('home');

Route::middleware(['auth', 'verified'])->group(function () {
    Route::inertia('dashboard', 'Dashboard')->name('dashboard');
    Route::resource('/users', UserController::class);

    // PoC Calendars
    Route::inertia('poc/fullcalendar', 'poc/FullCalendar/Index')->name('poc.fullcalendar');
});

require __DIR__ . '/settings.php';

