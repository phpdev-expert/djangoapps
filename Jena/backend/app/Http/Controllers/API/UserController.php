<?php

namespace App\Http\Controllers\API;


use Illuminate\Http\Request;
use App\Http\Controllers\API\BaseController as BaseController;
use App\User;
use Validator;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;


class UserController extends BaseController
{

    protected $storageImagePath;
    public function __construct()
    {
        $this->storageImagePath = url('/').'/storage/app/';
    }


    /**
     * Display a listing of the resource.
     *
     * @return \Illuminate\Http\Response
     */
    public function index(Request $request)
    {
      $email = $request->input('email');
      $password = $request->input('password');
      $user = User::where('email', '=', $email)->first();
      if (!$user) {
        return response()->json(['status'=>0, 'message' => 'Login Faieeel, please check email id']);
      }
      if (!Hash::check($password, $user->password)) {
        return response()->json(['status'=>0, 'message' => 'Login Faieeeel, pls check password']);
      }
        return response()->json(['status'=>1,'message'=>'success successfully', 'data' => $user]);
    }


    /**
     * Store a newly created resource in storage.
     *
     * @param  \Illuminate\Http\Request  $request
     * @return \Illuminate\Http\Response
     */
    public function store(Request $request)
    {
      $email = $request->input('email');
      $password = $request->input('password');
      $user = User::where('email', '=', $email)->first();
      if (!$user) {
        return response()->json(['status'=>0, 'message' => 'Login Fail, please check email id']);
      }
      if (!Hash::check($password, $user->password)) {
        return response()->json(['status'=>0, 'message' => 'Login Fail, pls check password']);
      }
        return response()->json(['status'=>1,'message'=>'success', 'data' => $user]);
    }

    public function uploadImage($file){
          $file = $file;
          $path = $file->path();
          $extension = $file->extension();
          $pathUploadImage=$file->store('images');
          return $this->storageImagePath.$pathUploadImage;
    }



}

 ?>
