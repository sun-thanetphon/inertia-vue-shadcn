<?php

namespace Tests\Feature;

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Inertia\Testing\AssertableInertia as Assert;
use Tests\TestCase;

class PocCalendarTest extends TestCase
{
    use RefreshDatabase;

    public function test_unauthenticated_user_cannot_access_poc_calendars(): void
    {
        $this->get('/poc/fullcalendar')->assertRedirect('/login');
        $this->get('/poc/vue-cal')->assertRedirect('/login');
    }

    public function test_authenticated_user_can_access_fullcalendar_poc(): void
    {
        $user = User::first() ?? User::factory()->create();

        $response = $this->actingAs($user)->get('/poc/fullcalendar');

        $response->assertStatus(200);
        $response->assertInertia(fn (Assert $page) => $page
            ->component('poc/FullCalendar/Index')
        );
    }

    public function test_authenticated_user_can_access_vue_cal_poc(): void
    {
        $user = User::first() ?? User::factory()->create();

        $response = $this->actingAs($user)->get('/poc/vue-cal');

        $response->assertStatus(200);
        $response->assertInertia(fn (Assert $page) => $page
            ->component('poc/VueCal/Index')
        );
    }
}
