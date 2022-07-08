using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using Emgu.CV;
using Emgu.CV.Structure;
using Emgu.CV.UI;
using Emgu.CV.CvEnum;
using Emgu.CV.Util;
using Tesseract;
namespace Vietnamese_License_Plate_Recognition
{
    public partial class Form1 : Form
    {
        List<Image<Bgr, Byte>> PlateImagesList = new List<Image<Bgr, byte>>();
        List<Rectangle> listRect = new List<Rectangle>();
        public Form1()
        {
            InitializeComponent();
        }
        const int Maxtrix = 3;//3x3
        private void button1_Click(object sender, EventArgs e)
        {
            // open file dialog   
            OpenFileDialog open = new OpenFileDialog();
            // image filters  
            open.Filter = "Image Files(*.jpg; *.jpeg; *.gif; *.bmp)|*.jpg; *.jpeg; *.gif; *.bmp";
            if (open.ShowDialog() == DialogResult.OK)
            {
                // display image in picture box  
                string startupPath = open.FileName;
                Image<Rgb, Byte> img = new Image<Rgb, Byte>(startupPath);
                imageBox1.Image = img;
                Image<Gray, Byte> imgGray = new Image<Gray, Byte>(startupPath);
                pictureBox1.Image = imgGray.ToBitmap();
                ProcessImage(startupPath);
            }
        }

        public void ProcessImage(string startupPath)
        {
            Bitmap image = new Bitmap(startupPath);
            FindLicensePlate(image, pictureBox1, imageBox1, PlateImagesList, panel1);
        }
        //Hàm xử lý biển số xe 
        public void FindLicensePlate(Bitmap image, PictureBox pictureBox1, ImageBox imageBox1, List<Image<Bgr, byte>> plateImagesList, Panel panel1)
        {
            try
            {
                //Detect biển số xe
                Image<Bgr, byte> image2 = new Image<Bgr, byte>(image);
                CascadeClassifier classifier = new CascadeClassifier(Application.StartupPath + "\\output-hv-33-x25.xml");
                var imgGray = image2.Convert<Gray, byte>().Clone();
                Rectangle[] plates = classifier.DetectMultiScale(imgGray, 1.1, 4);
                if (plates.Length == 0)
                {
                    MessageBox.Show("Không thể nhận dạng được biển số xe này !", "TD SJC");
                    return;
                }

                foreach (Rectangle plate in plates)
                {
                    if (plate.Width > 30 && plate.Width < 250 && plate.Height >10 && plate.Height < 250)
                    {
                        image2.Draw(plate, new Bgr(0, 255, 0), 2);
                        imageBox1.Image = image2;
                        Image<Bgr, byte> image3 = new Image<Bgr, byte>(image);
                        image3.ROI = plate;
                        pictureBox1.Image = image3.Bitmap;
                        Console.WriteLine("W: {0}, H: {1}", plate.Width, plate.Height);
                    }      
                    else
                    {
                        MessageBox.Show("Không nhận diện được. Thử lại ảnh khác !", "TD SJC");
                        return;
                    }    
                }
                //Tìm Contours cho biển số vừa detect được
                Image<Bgr, byte> src = new Image<Bgr, byte>(new Bitmap(pictureBox1.Image));
                IdentifyContours(src, out listRect);
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }
        }
        public static string OCR(Bitmap image)
        {
            string ocrtext = "";
            using (var engine = new TesseractEngine(@"./data", "eng", EngineMode.Default))
            {
                using (var img = PixConverter.ToPix(image))
                {
                    using (var page = engine.Process(img))
                    {
                        ocrtext = page.GetText();
                    }
                }
            }
            return ocrtext;
            //var ocr = new TesseractEngine(@"./data", "eng", EngineMode.Default);
            //var page = ocr.Process(image);
            //return page.GetText();
        }
        public void IdentifyContours(Image<Bgr,byte> colorImage, out List<Rectangle> listRect)
        {
            List<Rectangle> listContour = new List<Rectangle>();        
            Image<Gray, byte> srcGray = colorImage.Convert<Gray, byte>();
            Image<Gray, byte> imageT = new Image<Gray, byte>(srcGray.Width, srcGray.Height);
            CvInvoke.AdaptiveThreshold(srcGray, imageT, 255.0, AdaptiveThresholdType.MeanC, ThresholdType.Binary, 45, 2.0);
            pictureBox3.Image = imageT.Bitmap;
            Image<Gray, byte> imageThresh = imageT;
            imageT = imageT.ThresholdBinary(new Gray(100), new Gray(255.0));//Cần xử lý thêm để nhận dạng tốt hơn
            VectorOfVectorOfPoint contour = new VectorOfVectorOfPoint();
            Mat hier = new Mat();
            CvInvoke.FindContours(imageT, contour, hier, RetrType.List, ChainApproxMethod.ChainApproxSimple);
            Dictionary<int, double> dict = new Dictionary<int, double>();
            //Console.WriteLine(contour.Size);
            if (contour.Size > 0)
            {
                string textPlate = "";       
                for (int i = 0; i < contour.Size; i++)
                {         
                    Rectangle rect = CvInvoke.BoundingRectangle(contour[i]);                   
                    double area = CvInvoke.ContourArea(contour[i]);
                    double rate = (double)rect.Width / (double)rect.Height;
                    if (rect.Width > 5 && rect.Width <50 && rect.Height >= 15 && rect.Height < 50 && rate > 0.2 && rate < 1)
                    {
                        //Console.WriteLine("W: {0}, H: {1}, Rate W/H: {2}, Area: {3}", rect.Width, rect.Height, rate, area);
                        CvInvoke.Rectangle(colorImage, rect, new MCvScalar(255, 0, 0),1);
                        Image<Gray, byte> imageCrop = imageThresh;
                        imageCrop.ROI = rect;
                        Image<Gray, byte> resizedImage = imageCrop.Resize(50, 90, Inter.Linear);                       
                        Mat imgCropResize = resizedImage.Mat;               
                        CvInvoke.Imshow("Numbers Plate", imgCropResize);
                        textPlate += OCR(resizedImage.Bitmap);
                        Console.Write(textPlate);
                        //CvInvoke.Imwrite("Numbers Plate.png", imgCropResize);
                        //Image<Gray, Byte> imgFinal = new Image<Gray, Byte>("Numbers Plate.png");
                        CvInvoke.WaitKey(0);
                        dict.Add(i, area);                      
                    }                  
                }
                //textPlate = GetText(new Bitmap(pictureBox3.Image));
                //MessageBox.Show(textPlate);
            }   
            var item = dict.OrderByDescending(v => v.Value);  
            pictureBox2.Image = colorImage.Bitmap;
            //textBox1.Text = item.ElementAt(1).Value.ToString(); 
            //return out
            listRect = null;
        }
        
    }
}
