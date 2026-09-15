<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Inertia\Inertia;

class ReaderCardController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        return Inertia::render('ReaderCards/Index');
    }

    /**
     * Show the form for creating a new resource.
     */
    public function create()
    {
        //
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        //
    }

    /**
     * Display the specified resource.
     */
    public function show(string $id)
    {
        sleep(5);

        $mockCardData = [
            'national_id' => "1189500695886",
            'prefix_th' => 'นาย',
            'firstname_th' => 'ธเนศพล',
            'lastname_th' => 'โหนกระสวย',
            'prefix_en' => 'Mr.',
            'firstname_en' => 'Thanetphon',
            'lastname_en' => 'honkasuay',
            'birth_date' => '1990-05-15',
            'gender' => 'ชาย',
            'address' => '123/45 ถนนสุขุมวิท แขวงคลองเตย เขตคลองเตย กรุงเทพมหานคร 10110',
            'issue_date' => '2020-01-01',
            'expire_date' => '2030-12-31',
            'chip_id' => 'THID987654321098',
        ];


        return Inertia::render('ReaderCards/Index', [
            'cardData' => $mockCardData
        ]);
    }

    /**
     * Show the form for editing the specified resource.
     */
    public function edit(string $id)
    {
        //
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, string $id)
    {
        //
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(string $id)
    {
        //
    }
}
